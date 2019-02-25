my_overflow: my_overflow.c
	gcc -fno-stack-protector -c -g ./my_overflow.c -o my_overflow.o
	ld -N -z execstack my_overflow.o -o a.out
