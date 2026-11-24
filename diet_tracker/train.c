
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

// Passenger Node (Circular Linked List)
struct Passenger {
    int id;
    char name[50];
    int age;
    struct Passenger *next;
};

// Coach Node (Singly Linked List)
struct Coach {
    int coachNo;
    char coachType[30];
    struct Passenger *passengers;
    struct Coach *next;
};

struct Coach *head = NULL;

// Function to add coach
void addCoach() {
    struct Coach *newCoach, *temp;

    newCoach = (struct Coach*)malloc(sizeof(struct Coach));

    printf("Enter Coach Number: ");
    scanf("%d", &newCoach->coachNo);

    printf("Enter Coach Type (Sleeper/AC/General): ");
    scanf("%29s", newCoach->coachType);

    newCoach->passengers = NULL;
    newCoach->next = NULL;

    if (head == NULL) {
        head = newCoach;
    } else {
        temp = head;

        while (temp->next != NULL) {
            temp = temp->next;
        }

        temp->next = newCoach;
    }

    printf("\nCoach Added Successfully!\n");
}

// Function to display coaches
void displayCoaches() {
    struct Coach *temp = head;

    if (head == NULL) {
        printf("\nNo Coaches Available!\n");
        return;
    }

    printf("\n--- Train Coaches ---\n");

    while (temp != NULL) {
        printf("Coach No: %d | Type: %s\n",
               temp->coachNo, temp->coachType);

        temp = temp->next;
    }
}

// Function to find coach
struct Coach* findCoach(int number) {
    struct Coach *temp = head;

    while (temp != NULL) {
        if (temp->coachNo == number) {
            return temp;
        }

        temp = temp->next;
    }

    return NULL;
}

// Function to add passenger
void addPassenger() {
    int number;

    printf("Enter Coach Number: ");
    scanf("%d", &number);

    struct Coach *coach = findCoach(number);

    if (coach == NULL) {
        printf("\nCoach Not Found!\n");
        return;
    }

    struct Passenger *newPassenger, *temp;

    newPassenger = (struct Passenger*)
                   malloc(sizeof(struct Passenger));

    printf("Enter Passenger ID: ");
    scanf("%d", &newPassenger->id);

    printf("Enter Passenger Name: ");
    scanf("%49s", newPassenger->name);

    printf("Enter Passenger Age: ");
    scanf("%d", &newPassenger->age);

    if (coach->passengers == NULL) {
        coach->passengers = newPassenger;
        newPassenger->next = newPassenger;
    } else {
        temp = coach->passengers;

        while (temp->next != coach->passengers) {
            temp = temp->next;
        }

        temp->next = newPassenger;
        newPassenger->next = coach->passengers;
    }

    printf("\nPassenger Added Successfully!\n");
}

// Function to display passengers
void displayPassengers() {
    int number;

    printf("Enter Coach Number: ");
    scanf("%d", &number);

    struct Coach *coach = findCoach(number);

    if (coach == NULL) {
        printf("\nCoach Not Found!\n");
        return;
    }

    struct Passenger *temp = coach->passengers;

    if (temp == NULL) {
        printf("\nNo Passengers in this Coach!\n");
        return;
    }

    printf("\n--- Passenger Details ---\n");

    do {
        printf("ID: %d | Name: %s | Age: %d\n",
               temp->id, temp->name, temp->age);

        temp = temp->next;

    } while (temp != coach->passengers);
}

// Function to search passenger
void searchPassenger() {
    int number, id, found = 0;

    printf("Enter Coach Number: ");
    scanf("%d", &number);

    struct Coach *coach = findCoach(number);

    if (coach == NULL) {
        printf("\nCoach Not Found!\n");
        return;
    }

    printf("Enter Passenger ID: ");
    scanf("%d", &id);

    struct Passenger *temp = coach->passengers;

    if (temp == NULL) {
        printf("\nNo Passengers Available!\n");
        return;
    }

    do {
        if (temp->id == id) {
            printf("\nPassenger Found!\n");
            printf("Name: %s\n", temp->name);
            printf("Age: %d\n", temp->age);
            found = 1;
            break;
        }

        temp = temp->next;

    } while (temp != coach->passengers);

    if (!found) {
        printf("\nPassenger Not Found!\n");
    }
}

// Function to delete passenger
void deletePassenger() {
    int number, id;

    printf("Enter Coach Number: ");
    scanf("%d", &number);

    struct Coach *coach = findCoach(number);

    if (coach == NULL || coach->passengers == NULL) {
        printf("\nCoach or Passenger Not Found!\n");
        return;
    }

    printf("Enter Passenger ID to Delete: ");
    scanf("%d", &id);

    struct Passenger *current = coach->passengers;
    struct Passenger *previous = NULL;

    do {
        if (current->id == id) {

            if (current->next == current) {
                coach->passengers = NULL;
            } else {
                if (previous == NULL) {
                    struct Passenger *last = current;

                    while (last->next != current) {
                        last = last->next;
                    }

                    coach->passengers = current->next;
                    last->next = coach->passengers;
                } else {
                    previous->next = current->next;
                }
            }

            free(current);
            printf("\nPassenger Deleted Successfully!\n");
            return;
        }

        previous = current;
        current = current->next;

    } while (current != coach->passengers);

    printf("\nPassenger Not Found!\n");
}

// Function to delete coach
void deleteCoach() {
    int number;

    printf("Enter Coach Number to Delete: ");
    scanf("%d", &number);

    struct Coach *current = head;
    struct Coach *previous = NULL;

    while (current != NULL) {

        if (current->coachNo == number) {

            if (previous == NULL) {
                head = current->next;
            } else {
                previous->next = current->next;
            }

            // Free passengers
            struct Passenger *p = current->passengers;

            if (p != NULL) {
                struct Passenger *nextPassenger;

                while (p->next != current->passengers) {
                    nextPassenger = p->next;
                    free(p);
                    p = nextPassenger;
                }

                free(p);
            }

            free(current);

            printf("\nCoach Deleted Successfully!\n");
            return;
        }

        previous = current;
        current = current->next;
    }

    printf("\nCoach Not Found!\n");
}

// Main function
int main() {
    int choice;

    do {
        printf("\n===== TRAIN COACH MANAGEMENT SYSTEM =====\n");
        printf("1. Add Coach\n");
        printf("2. Display Coaches\n");
        printf("3. Add Passenger\n");
        printf("4. Display Passengers\n");
        printf("5. Search Passenger\n");
        printf("6. Delete Passenger\n");
        printf("7. Delete Coach\n");
        printf("8. Exit\n");

        printf("\nEnter Your Choice: ");
        scanf("%d", &choice);

        switch (choice) {

            case 1:
                addCoach();
                break;

            case 2:
                displayCoaches();
                break;

            case 3:
                addPassenger();
                break;

            case 4:
                displayPassengers();
                break;

            case 5:
                searchPassenger();
                break;

            case 6:
                deletePassenger();
                break;

            case 7:
                deleteCoach();
                break;

            case 8:
                printf("\nThank You for Using System!\n");
                break;

            default:
                printf("\nInvalid Choice!\n");
        }

    } while (choice != 8);

    return 0;
}
