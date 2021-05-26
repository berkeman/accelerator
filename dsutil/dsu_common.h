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

/**
 * This is the common part of a compressor module
 * #define DSU_NAME to the name of the compressor, include this file and
 * implement the six functions.
 * Look in compressor_none.c for an example.
 **/

#define PY_SSIZE_T_CLEAN 1
#include <Python.h>
#include <stdint.h>

#include "dsu.h"

struct ctx;
typedef struct ctx ctx;

static int dsu_read(ctx *ctx, char *buf, int *len);
static int dsu_write(ctx *ctx, const char *buf, int len);
static ctx *dsu_read_open(int fd, Py_ssize_t size_hint);
static ctx *dsu_write_open(int fd);
static void dsu_read_close(ctx *ctx);
static int dsu_write_close(ctx *ctx);

static dsu_compressor dsu = {
	(dsu_read_f       ) dsu_read,
	(dsu_write_f      ) dsu_write,
	(dsu_read_open_f  ) dsu_read_open,
	(dsu_write_open_f ) dsu_write_open,
	(dsu_read_close_f ) dsu_read_close,
	(dsu_write_close_f) dsu_write_close,
	DSU_MAGIC, 0
};

// Don't you just love the C preprocessor?
#define _str(s) #s
#define str(s) _str(s)
#define _paste(a, b) a ## b
#define paste(a, b) _paste(a, b)

#define MODNAME "_compressor_" str(DSU_NAME)

#if PY_MAJOR_VERSION < 3
#	define INITFUNC paste(init_compressor_, DSU_NAME)
#	define INITERR
#else
#	define INITFUNC paste(PyInit__compressor_, DSU_NAME)
#	define INITERR 0
	static struct PyModuleDef moduledef = {
		PyModuleDef_HEAD_INIT,
		MODNAME
	};
#endif

__attribute__ ((visibility("default"))) PyMODINIT_FUNC INITFUNC(void)
{
#if PY_MAJOR_VERSION < 3
	PyObject *m = Py_InitModule(MODNAME, 0);
#else
	PyObject *m = PyModule_Create(&moduledef);
#endif
	if (!m) return INITERR;
	dsu.name = PyUnicode_FromString(str(DSU_NAME));
	if (!dsu.name) return INITERR;
	PyObject *capsule = PyCapsule_New(
		(void *)&dsu,
		"accelerator." MODNAME ".capsule",
		0
	);
	if (!capsule) return INITERR;
	PyModule_AddObject(m, "capsule", capsule);
#if PY_MAJOR_VERSION >= 3
	return m;
#endif
}
