public class Main {

    private static class Node {
        public int data;
        public Node next;

        public Node(int d) {
            data = d;
            next = this;
        }
    }

    private static class PriorityTable {
        public static final int MAXPRIO = 10;

        private Node priorityTable[] = new Node[MAXPRIO + 1];

        public PriorityTable() {
            // bug: should be <=
            for (int i = 0; i < MAXPRIO; i++) {
                priorityTable[i] = new Node(-1);
            }
        }

        private void insert(int prio, int val) {
            Node n = new Node(val);

            n.next = priorityTable[prio].next;
            priorityTable[prio].next = n;
        }

        public String toString() {
            String s = "";
            for (int i = 0; i < MAXPRIO; i++) {
                Node n = priorityTable[i];
                Node next = n.next;
                s += "prio " + i + ": ";
                while (next != n) {
                    s += next.data + " ";
                    next = next.next;
                }
                s += "\n";
            }
            return s;
        }
    }


    private static void passingTests() {
        // passing test cases. Work for all cases where prio < MAXPRIO
        PriorityTable table = new PriorityTable();
        table.insert(5, 1);
        table.insert(5, 2);
        table.insert(1, 3);
        table.insert(2, 3);
        table.insert(4, 4);
        table.insert(8, 9);

        table = new PriorityTable();
        table.insert(9, 10);
        table.insert(0, 2);
        table.insert(1, 0);
    }

    private static void failingTests() {
        PriorityTable table = new PriorityTable();
        // error
        table.insert(10, 4);
    }

    public static void main(String[] args) {
        passingTests();

        try {
            failingTests();
        } catch (Exception e) {
            e.printStackTrace();
        }
    }
}
