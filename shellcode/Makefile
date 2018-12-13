all: shellcode

shellcode:
	as -g -o shellcode.o shellcode.s
	# code is not in stack, so make .text writable
	ld -N -z execstack shellcode.o
	./a.out

test:
	gcc -g -z execstack -fno-stack-protector test_shellcode.c

clean:
	rm -f ./a.out *.o
