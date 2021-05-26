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

typedef int (*dsu_read_f)(void *ctx, char *buf, int *len);
typedef int (*dsu_write_f)(void *ctx, const char *buf, int len);
typedef void *(*dsu_read_open_f)(int fd, Py_ssize_t size_hint);
typedef void *(*dsu_write_open_f)(int fd);
typedef void (*dsu_read_close_f)(void *ctx);
typedef int (*dsu_write_close_f)(void *ctx);

typedef struct dsu_compressor {
	dsu_read_f        read;
	dsu_write_f       write;
	dsu_read_open_f   read_open;
	dsu_write_open_f  write_open;
	dsu_read_close_f  read_close;
	dsu_write_close_f write_close;
	int64_t           magic;
	PyObject          *name;
} dsu_compressor;

#define DSU_MAGIC 0xb98ecfa63b83c602LL
