.data
# sh:
#     .asciz "/bin/sh"

.global _start

.text
_start:
    xorl %eax, %eax
    jmp next
sh:
    .asciz "/bin/sh"
next:
    movb $59, %al
    leaq sh(%rip), %rdi
    xorl %edx, %edx
    xorl %esi, %esi
    syscall

    movq $60, %rax
    movq $0, %rdi
    syscall
