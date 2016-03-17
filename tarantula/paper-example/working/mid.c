#include <stdio.h>

int mid(int x, int y, int z) {
    int m = z;
    if (y<z)
    {
        if (x<y)
            m = y;
        else if (x<z)
            m = x;
    }
    else {
        if (x>y)
            m = y;
        else if (x>z)
            m = x;
    }

    return m;

}

int main() {
    int x, y, z;
    scanf("%d %d %d", &x, &y, &z);
    int m = mid(x,y,z);
    printf("Middle number is %d\n", m);
}

