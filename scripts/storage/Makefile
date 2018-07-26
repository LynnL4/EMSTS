# tary, 12:49 2018/7/25

NAME=storage_tst

${NAME}: ${NAME}.c csapp.c
	gcc -o $@ $^ -lpthread

install: ${NAME}
	install ${NAME} /usr/bin

clean:
	rm -f ${NAME}
