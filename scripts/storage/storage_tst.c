// tary, 9:51 2012-8-9
#include <stdint.h>
#include <stdio.h>
#include <string.h>
#include <stdlib.h>
#include <fcntl.h>
#include <unistd.h>
#include <linux/limits.h>
#include <sys/stat.h>
#include <sys/time.h>
#include <getopt.h>
#include "csapp.h"

#define SF_CHK_SIZE		(0x100000)
#define SF_CHK_CNT		0x100

static unsigned sf_buf[SF_CHK_SIZE];
static unsigned sf_chk[SF_CHK_SIZE];
static size_t sf_size = sizeof sf_buf / sizeof sf_buf[0];
static size_t sf_cnt = SF_CHK_CNT;
static size_t sf_read = 1;
static uint64_t seed;
static long milli_w, milli_r;

static unsigned random_u(void) {
	seed = (seed * 0x5DEECE66DULL + 11ULL) % (0x1ULL << 48);
	return seed;
}

static int thunk_fill(unsigned* buf, int size) {
	int i;

	for (i = 0; i < size; i++) {
		buf[i] = random_u();
	}
	return 0;
}

static int storage_file_store(int fd) {
	int i;
	ssize_t size;

	seed = 0ULL;

	for (i = 0; i < sf_cnt; i++) {
		thunk_fill(sf_buf, sf_size);
		size = rio_writen(fd, sf_buf, SF_CHK_SIZE);
		if (size != SF_CHK_SIZE) {
			perror("write");
			return -1;
		}
	}

	return 0;
}

static int storage_file_check(int fd) {
	int i;
	ssize_t size;

	seed = 0ULL;

	for (i = 0; i < sf_cnt; i++) {
		size = rio_readn(fd, sf_buf, SF_CHK_SIZE);
		if (size != SF_CHK_SIZE) {
			perror("read");
			return -1;
		}
		thunk_fill(sf_chk, sf_size);
		if (memcmp(sf_buf, sf_chk, SF_CHK_SIZE) != 0) {
			fprintf(stderr, "file compare fail\n");
			return -1;
		}
	}
	return 0;
}

long get_milli_secs(struct timeval* start, struct timeval* end) {
	struct timeval diff;
	long milli;

	timersub(start, end, &diff);
	milli = diff.tv_sec * 1000 + diff.tv_usec / 1000;
	return milli;
}

int storage_test(const char* path) {
	int fd, fd_c;
	int i;
	char file_name[PATH_MAX];
	char *cache_name = "/proc/sys/vm/drop_caches";
	mode_t mask;
	struct timeval tv_b, tv_e;

	strcpy(file_name, path);
	strcat(file_name, "/storage_test_file.bin");

	mask = S_IRUSR | S_IWUSR | S_IRGRP | S_IWGRP | S_IROTH | S_IWOTH;
	gettimeofday(&tv_b, NULL);
	fd = open(file_name, O_WRONLY | O_CREAT | O_SYNC, mask);
	if (fd == -1) {
		perror("open");
		return -1;
	}
	if (storage_file_store(fd) < 0) {
		return -1;
	}
	fsync(fd);
	close(fd);

	gettimeofday(&tv_e, NULL);
	milli_w = get_milli_secs(&tv_e, &tv_b);

	for (i = 0; i < sf_read; i++) {
		fd_c = open(cache_name, O_WRONLY | O_SYNC);
		if (write(fd_c, "3", 1) != 1) {	
                        perror("clean cache");
                        return -1;
                }
		fd = open(file_name, O_RDONLY);
		if (fd == -1) {
			perror("open");
			return -1;
		}
		if (storage_file_check(fd) < 0) {
			return -1;
		}
		close(fd);
		close(fd_c);
	}
	gettimeofday(&tv_b, NULL);
	milli_r = get_milli_secs(&tv_b, &tv_e);

	remove(file_name);
	return 0;
}

static int usage(const char* name) {
	printf("Usage: %s [options] path\n", name);
	printf("Supported options:\n");
	printf("\t-n size  per MB\n");
	printf("\t-r read-times read times\n");
	printf("\tpath      target test directory\n");
	return 0;
}

int main(int argc, char* const argv[]) {
	int ch;

	while ((ch = getopt(argc, argv, "n:r:")) != -1) {
		switch(ch) {
		case 'n':
			sf_cnt = atoi(optarg);
			break;
		case 'r':
			sf_read = atoi(optarg);
			break;
		default:
			usage(argv[0]);
			return -1;
		}
	}
	if (optind >= argc) {
		usage(argv[0]);
		return -1;
	}

	if (storage_test(argv[optind]) < 0) {
		fprintf(stderr, "storage test fail\n");
		// perror("storage_test");
		return -1;
	}
	fprintf(stderr, "storage test ok\n");

	fprintf(stderr, "Write %lu MB, %.3lf MB/s\n", sf_cnt, 1000.0 * sf_cnt / milli_w);
	fprintf(stderr, "Read  %lu MB * %lu times\n", sf_cnt, sf_read);
	fprintf(stderr, "      average %.3lf MB/s\n", 1000.0 * sf_cnt * sf_read / milli_r);
	return 0;
}
