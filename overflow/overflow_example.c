#include <string.h>
#include <stdio.h>

void process(char *param) {
    char buf[25];

    strcpy(buf, param);
}

int main() {
    char global_buf[100];
    scanf("%s", global_buf);
    process(global_buf);

    printf("all normal");
}
