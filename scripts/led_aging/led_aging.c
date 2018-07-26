// tary, 10:24 2012-07-04
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/sysinfo.h>
#include <ctype.h>
#include <errno.h>
#include <unistd.h>
#include <fcntl.h>
#include <time.h>
#include <pthread.h>
#include "led_aging.h"

#ifndef USE_PTHREAD
#error be define USE_PTHREAD to 0 or 1!!!
#endif

#define DBG			0
#define MAX_LED_CNT		8
#define BUF_SIZE		1024
#define MMAX_SIZE		1000
#define AGING_METHOD_TICK	10
#define WARN_DELAY		50	// milli second

typedef struct {
	int led_nr;
	int delay;	// milli second
	int init_delay;
	int state;
} led_arg_t;

static int led_cnt = 1;
static const char* led_file[MAX_LED_CNT] = {
	"/sys/class/leds/led1/brightness",
};
static led_arg_t led_args[MAX_LED_CNT];
static char* self_path = "/usr/bin/led_aging";
static char* post_script = NULL;
static int aging_seconds = 0;

#if USE_PTHREAD
static volatile int f_exit = 0;
static volatile int mem_err = 0;
#endif

#if USE_PTHREAD
static int led_onoff(int nr, int on_n_off) {
	char s_cmd[1024];
	int on = !!on_n_off;

	if (nr < 0 || nr >= led_cnt) return -1;

	sprintf(s_cmd, "echo -n %d > %s", on, led_file[nr]);
	system(s_cmd);

	return 0;
}

static unsigned long fibonacci(int order) {
	unsigned long a, b, c;
	int i;

	a = b = 1;

	if (order <= 2) return b;

	for (i = 2; i < order; i++) {
		c = a + b;
		a = b;
		b = c;
	}

	return c;
}

static int alloc_test(void* t_array[], int max_size) {
	int i, j;
	char* p;

	for (i = 1; i < max_size; i++) {
		t_array[i] = malloc(i);
		if (t_array[i] == 0) {
			return i;
		}

		p = (char*)t_array[i];
		for (j = 0; j < i; j++) {
			p[j] = j;
		}
	}
	return 0;
}

static int free_test(void* t_array[], int max_size) {
	int i, j;
	char* p;

	#if 0
	static int s = 0;

	if (s++ > 200) {
		return -1;
	}
	#endif


	for (i = 1; i < max_size; i++) {
		if (t_array[i] == 0) break;

		p = (char*)t_array[i];
		for (j = 0; j < i; j++) {
			if (p[j] != (char)(j & 0xFF)) {
				return -1;
			}
		}

		free(t_array[i]);
	}
	return 0;
}

static void* led_thread(void* arg) {
	led_arg_t* led_arg = (led_arg_t*)arg;
	void* t_array[MMAX_SIZE];
	int on = 0;

	while (!f_exit) {
		alloc_test(t_array, MMAX_SIZE);

		led_onoff(led_arg->led_nr, on);
		usleep(led_arg->delay * 1000);
		on = !on;

		if (free_test(t_array, MMAX_SIZE) < 0) {
			mem_err |= 1;
			break;
		}
	}

	on = 0;
	led_onoff(led_arg->led_nr, on);

	return 0;
}

static int aging_method(int interval) {
	pthread_t tids[MAX_LED_CNT];
	struct sysinfo info;
	int i, err;

	for (i = 0; i < led_cnt; i++) {
		led_args[i].led_nr = i;
		led_args[i].delay = (i + 3) * 100;
		err = pthread_create(&tids[i], NULL, led_thread, &led_args[i]);
		if (err != 0) {
			perror("pthread_create\n");
			exit(1);
		}
	}

	do {
		for (i = 0; i < 1000000; i++) {
			fibonacci(30);
		}

		usleep(1000);

		if (mem_err) break;

                if (sysinfo(&info)) {
                        fprintf(stderr, "Failed to get sysinfo, errno:%u, reason:%s\n",
                                        errno, strerror(errno));
                        return -1;
                }

		#if DBG
		printf("Seconds since boot %ld\n", info.uptime);
		#endif
	} while (info.uptime <= interval);

	f_exit = 1;

	for (i = 0; i < led_cnt; i++) {
		void* tr;

		pthread_join(tids[i], &tr);
	}

	if (mem_err) {
		exit(2);
	}

	return 0;
}
#else

static int led_onoff(int nr, int on_n_off) {
	unsigned char data;

	data = on_n_off? '1': '0';
	write(led_args[nr].led_nr, &data, sizeof data);

	return 0;
}

static int aging_method(int interval) {
	struct sysinfo info;
	int i;

	for (i = 0; i < led_cnt; i++) {
		if ((led_args[i].led_nr = open(led_file[i], O_RDWR)) < 0) {
			fprintf(stderr, "open file %s error\n", led_file[i]);
			exit(3);
		}
		led_args[i].init_delay = (i + 3) * 100;
		led_args[i].delay = led_args[i].init_delay;
		led_args[i].state = 0;

		led_onoff(i, led_args[i].state);
	}

	do {
		usleep(AGING_METHOD_TICK * 1000);

		for (i = 0; i < led_cnt; i++) {
			led_args[i].delay -= AGING_METHOD_TICK;
			if (led_args[i].delay <= 0) {
				led_args[i].delay = led_args[i].init_delay;
				led_args[i].state = !led_args[i].state;
				led_onoff(i, led_args[i].state);
			}
		}

		if (sysinfo(&info)) {
			fprintf(stderr, "Failed to get sysinfo, errno:%u, reason:%s\n",
					errno, strerror(errno));
			return -1;
		}

		#if DBG
		printf("Seconds since boot %ld\n", info.uptime);
		#endif
	} while (info.uptime <= interval);

	for (i = 0; i < led_cnt; i++) led_onoff(i, 0);

	return 0;
}
#endif //USE_PTHREAD

static int led_warn(void) {
	int i;

	for(;;) {
		for (i = 0; i < led_cnt; i++) led_onoff(i, 1);
		usleep(WARN_DELAY * 1000);
		for (i = 0; i < led_cnt; i++) led_onoff(i, 0);
		usleep(WARN_DELAY * 1000);
	}
	return 0;
}

static int ledacc_config(void) {
	char buf[BUF_SIZE], *p;
	FILE *f;
	int leds = 0;
	char *conffile;

	if((conffile = getenv("LEDACC_CONFFILE")) == NULL) {
		conffile = strdup ("/etc/led_aging.conf");
	}

	f = fopen(conffile, "r");
	if (!f) {
		perror("open config file");
		exit(1);
	}

	buf[BUF_SIZE - 2] = '\0';
	while ((p = fgets(buf, BUF_SIZE, f)) != NULL) {
		char* e;
		char* tok;

		e = strchr(p, '\n');
		if (e) {
			*e = '\0';
		}

		if (buf[BUF_SIZE - 2] != '\0') {
			fprintf(stderr, "line too long:%s\n", buf);
			break;
		}

		tok = strtok(p, " \t");
		if (tok == NULL || *tok == '#') {
			continue;
		}

		e = tok + strlen(tok) + 1;
		if (strcmp(tok, "self_path") == 0) {
			self_path = strdup(e);
			#if DBG
			printf("self_path:%s\n", self_path);
			#endif
		} else if (strcmp(tok, "led") == 0) {
			if (leds >= MAX_LED_CNT) {
				continue;
			}
			#if DBG
			printf("led_file[%d]:%s\n", leds, e);
			#endif
			led_file[leds++] = strdup(e);
		} else if (strcmp(tok, "interval") == 0) {
			aging_seconds = atoi(e) * 60;
			#if DBG
			printf("aging_seconds: %d seconds\n", aging_seconds);
			#endif
		} else if (strcmp(tok, "post_script") == 0) {
			post_script = strdup(e);
			#if DBG
			printf("post_script:%s\n", post_script);
			#endif
		}
	}

	led_cnt = leds;

	if (aging_seconds == 0) {
		fprintf(stderr, "%s:undefined interval\n", conffile);
		exit(-1);
	}

	return 0;
}

int main(int argc, char *argv[]) {
	ledacc_config();

	printf("interval = %d second\n", aging_seconds);

	aging_method(aging_seconds);

	if (remove(self_path) == 0) {
		printf("%s removed\n", self_path);
	} else {
		perror("remove");
	}

	if (post_script) {
		system(post_script);
	}

	led_warn();

	return 0;
}
