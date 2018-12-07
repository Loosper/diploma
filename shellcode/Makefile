all: shellcode

shellcode:
	gcc -c shellcode.s
	ld shellcode.o
	./a.out
	
test:
	gcc -fno-stack-protector -z execstack test_shellcode.c
