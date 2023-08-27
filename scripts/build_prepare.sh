#!/bin/bash
# This is for running in a manylinux or similar docker image, so /bin/bash is fine.
#
# docker run -it -v /some/where:/out:ro -v /path/to/accelerator:/accelerator:ro --tmpfs /tmp:exec,size=1G quay.io/pypa/manylinux2010_x86_64:2021-02-06-c17986e /accelerator/scripts/build_prepare.sh
#
# build_wheels.sh will call this, but it's a separate script so you can run
# it once and save that docker image.

set -euo pipefail
set -x
shopt -s nullglob

test -d /accelerator/.git || exit 1
test -d /accelerator/accelerator || exit 1

VERSION=5
ENDIANNESS="$(/opt/python/cp39-cp39/bin/python3 -c 'import sys; print(sys.byteorder)')"

if [ ! -e /opt/python/cp310-cp310/bin/python ]; then
	if [ "$AUDITWHEEL_ARCH" = "x86_64" -o "$AUDITWHEEL_ARCH" = "i686" ]; then
		if [ ! -e /opt/python/cp27-cp27mu ]; then
			echo "Old build container needs python 2.7, run in manylinux2010_$AUDITWHEEL_ARCH:2021-02-06-c17986e or earlier"
			exit 1
		fi
	fi

	if [ ! -e /opt/python/cp35-cp35m ]; then
		echo "Old build container needs python 3.5, your manylinux container must be too new"
		exit 1
	fi
fi

if [ -e /prepare/.done ]; then
	if [ "$(cat /prepare/.done)" = "$VERSION" ]; then
		exit 0
	fi
fi

if [ ! -e "/out/old_versions.$VERSION.$ENDIANNESS.tar.gz" ]; then
	echo "First use build_old_versions.sh to produce /out/old_versions.$VERSION.$ENDIANNESS.tar.gz"
	exit 1
fi

rm -rf /prepare
mkdir /prepare

cd /prepare
tar zxf "/out/old_versions.$VERSION.$ENDIANNESS.tar.gz"

# The numeric_comma test needs a locale which uses numeric comma.
command -v localedef && localedef -i da_DK -f UTF-8 da_DK.UTF-8

# The Alpine based musl containers don't have tzdata installed
test -d /usr/share/zoneinfo || apk add tzdata

ZLIB_PREFIX="/prepare/zlib-ng"
/accelerator/scripts/build_zlib-ng.sh "$ZLIB_PREFIX"

cd /tmp

for V in /opt/python/cp[23][5-9]-* /opt/python/cp31[0-9]-*; do
	V="${V/\/opt\/python\//}"
	case "$V" in
		cp27-*)
			/opt/python/"$V"/bin/pip install virtualenv "setproctitle==1.1.8" "bottle==0.12.7" "waitress==1.0" "configparser==3.5.0" "monotonic==1.0" "selectors2==2.0.0" "build==0.5.1"
			;;
		*)
			# oldest deps we can use on manylinux2010, newest on others
			if [ "${AUDITWHEEL_PLAT/%_*}" = "manylinux2010" ]; then
				/opt/python/"$V"/bin/pip install "setproctitle==1.1.8" "bottle==0.12.7" "waitress==1.0" "build==0.5.1"
			else
				/opt/python/"$V"/bin/pip install setproctitle 'bottle>=0.12.7, <0.13' waitress
			fi
			;;
	esac
done


echo "$VERSION" >/prepare/.done

set +x

echo
echo OK
echo
