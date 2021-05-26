/**
 * Copyright (c) 2021 Carl Drougge
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *  http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 **/

#include <zlib.h>

#define DSU_NAME gzip
#include "dsu_common.h"

#define err1(v) if (v) goto err

typedef struct ctx {
	gzFile fh;
} ctx;

static ctx *dsu_read_open(int fd, Py_ssize_t size_hint)
{
	ctx *ctx;
	ctx = malloc(sizeof(*ctx));
	err1(!ctx);
	ctx->fh = gzdopen(fd, "rb");
	if (size_hint >= 0 && size_hint < 400000) {
		gzbuffer(ctx->fh, 16 * 1024);
	} else {
		gzbuffer(ctx->fh, 64 * 1024);
	}
	err1(!ctx->fh);
	return ctx;
err:
	if (ctx) free(ctx);
	return 0;
}

static int dsu_read(ctx *ctx, char *buf, int *len)
{
	err1(!ctx->fh);
	int got = gzread(ctx->fh, buf, *len);
	err1(got == -1);
	*len = got;
	return 0;
err:
	if (ctx->fh) {
		gzclose(ctx->fh);
		ctx->fh = 0;
	}
	return 1;
}

static void dsu_read_close(ctx *ctx)
{
	if (ctx->fh) gzclose(ctx->fh);
	free(ctx);
}

static ctx *dsu_write_open(int fd)
{
	ctx *ctx;
	ctx = malloc(sizeof(*ctx));
	err1(!ctx);
	ctx->fh = gzdopen(fd, "wb");
	err1(!ctx->fh);
	return ctx;
err:
	if (ctx) free(ctx);
	return 0;
}

static int dsu_write_close(ctx *ctx)
{
	int res = 1;
	err1(!ctx->fh);
	res = gzclose(ctx->fh);
err:
	free(ctx);
	return res;
}

static int dsu_write(ctx *ctx, const char *buf, int len)
{
	err1(!ctx->fh);
	int wrote = gzwrite(ctx->fh, buf, len);
	err1(wrote != len);
	return 0;
err:
	if (ctx->fh) {
		gzclose(ctx->fh);
		ctx->fh = 0;
	}
	return 1;
}
