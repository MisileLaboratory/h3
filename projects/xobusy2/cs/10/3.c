#include <stdio.h>

int main() {
    for (int i=0;i<5;i++) {
        for (int j=5;j>=1;j--) {
            printf("%3d", j+i*5);
        }
        printf("\n");
    }
}
