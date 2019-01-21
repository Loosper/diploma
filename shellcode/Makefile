all: shellcode

shellcode: shell.s
	as -g -o shellcode.o shell.s
	# code is not in stack, so make .text writable
	ld -N -z execstack shellcode.o

tcp: tcp_shell.s
	as -g -o tcp.o tcp_shell.s
	ld -N -z execstack tcp.o

xor: xor_shell.s
	as -g -o xor.o xor_shell.s
	ld -N -z execstack xor.o

test:
	gcc -g -z execstack -fno-stack-protector test_shellcode.c

clean:
	rm -f ./a.out *.o
