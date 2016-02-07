#include <stdio.h>
#include <malloc.h>

#define MAXPRIORITY 10


typedef struct NodeStruct {
    int data;

    struct NodeStruct* next;
    struct NodeStruct* prev;

} Node;

void list_init(Node* n) {
    n->data = -1;
    n->next = n;
}

void list_prepend(Node* existing, int new_data) {
    Node* newnode = malloc(sizeof(Node));
    newnode->data = new_data;
    newnode->next = existing->next;
    newnode->prev = existing;

    newnode->next->prev = newnode;
    existing->next = newnode;
}




void table_insert(Node* table, int prio, int value) {
    // constraint: &table[prio] always appears in the value set for list_init's arg
    list_prepend(&table[prio], value);
}

int initialize(Node* table) {
    // here is the bug: should be i <= MAXPRIORITY
    for (int i = 0; i < MAXPRIORITY; i++) {
        list_init(&table[i]);
    }
}


//
// used for debugging
//
void print_table(Node* table) {
    for (int i = 0; i < MAXPRIORITY; i++) {
        printf("List %d\n", i);
        Node* begin = &table[i];
        Node* n = begin->next;
        while (n != begin) {
            printf("%d ", n->data);
            n = n->next;
        }
        printf("\n");
    }
}

int main() {
    Node* table = malloc((MAXPRIORITY+1) * sizeof(Node));

    initialize(table);



    // successful cases
    table_insert(table, 5, 11);
    table_insert(table, 5, 0);
    table_insert(table, 5, 2);
    table_insert(table, 0, 3);

    table_insert(table, 9, 9);
    table_insert(table, 9, 9);
    table_insert(table, 9, 9);
    table_insert(table, 9, 9);

    // constraint: priority < MAXPRIO

    // failure on edge case!
    //table_insert(table, 10, 3);

    print_table(table);
}
