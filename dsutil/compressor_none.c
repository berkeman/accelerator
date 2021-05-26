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

#include <sys/types.h>
#include <sys/stat.h>
#include <fcntl.h>
#include <unistd.h>

#define DSU_NAME none
#include "dsu_common.h"

#define err1(v) if (v) goto err


typedef struct ctx {
	int fd;
} ctx;

static ctx *dsu_read_open(int fd, Py_ssize_t size_hint)
{
	ctx *ctx;
	ctx = malloc(sizeof(*ctx));
	err1(!ctx);
	ctx->fd = fd;
	return ctx;
err:
	if (ctx) free(ctx);
	return 0;
}

static int dsu_read(ctx *ctx, char *buf, int *len)
{
	err1(ctx->fd == -1);
	ssize_t got = read(ctx->fd, buf, *len);
	err1(got == -1);
	*len = got;
	return 0;
err:
	if (ctx->fd != -1) {
		close(ctx->fd);
		ctx->fd = -1;
	}
	return 1;
}

static void dsu_read_close(ctx *ctx)
{
	if (ctx->fd != -1) close(ctx->fd);
	free(ctx);
}

static ctx *dsu_write_open(int fd)
{
	return dsu_read_open(fd, 0);
}

static int dsu_write_close(ctx *ctx)
{
	int fd = ctx->fd;
	free(ctx);
	return close(fd);
}

static int dsu_write(ctx *ctx, const char *buf, int len)
{
	err1(ctx->fd == -1);
	int wrote = write(ctx->fd, buf, len);
	err1(wrote != len);
	return 0;
err:
	if (ctx->fd != -1) {
		close(ctx->fd);
		ctx->fd = -1;
	}
	return 1;
}
