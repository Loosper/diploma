.global _start

.text
_start:
    jmp next
addr:
    .quad 0xffffffffffffffff
addr_eol:
    .quad 0xffffffffffffffff
sh:
    .ascii "/bin/ls"
sh_eol:
    .byte 0xff

next:
    xorq %rax, %rax
    # stack is executable, i can do this
    movb %al, sh_eol(%rip)
    leaq sh(%rip), %rdi
    # init char *argvp[]
    movq %rax, addr_eol(%rip)
    movq %rdi, addr(%rip)
    leaq addr(%rip), %rsi
    xorl %edx, %edx
    # sys_execve
    movb $59, %al
    syscall

    # sys_exit
    xorl %eax, %eax
    movb $60, %al
    xorl %edi, %edi
    syscall
