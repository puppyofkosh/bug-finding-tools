import daikon.Quant;

public class Main {

    private static void start_loop_inv(int key, int a[], int lo, int mid, int hi) {
    }
    private static void end_loop_inv(int key, int a[], int lo, int mid, int hi) {
    }
    private static void reduce_hi_loop_inv(int key, int a[], int lo, int mid, int hi) {
    }
    private static void inc_lo_loop_inv(int key, int a[], int lo, int mid, int hi) {
    }

    private static void dummy_fn_reduce_hi(int key, int elem, int l, int m, int h) {
    }
    private static void dummy_fn_inc_lo(int key, int elem, int l, int m, int h) {
    }

    private static void return_fail_inv(int lo, int hi, int key, int[] arr) {
    }

    private static void before_loop(int lo, int hi, int key, int[] arr) {
    }

    public static int bsearch(int[] a, int key) {
        int lo = 0;
        // should be a.length - 1
        int hi = a.length;
        before_loop(lo, hi, key, a);
        while (lo <= hi) {
            int mid = lo + (hi - lo) / 2;
            // forces daikon to compute invariants about dummy_fn input and output,
            // which are in this case, loop invariants.
            start_loop_inv(key, a, lo, mid, hi);

            // mid <= size(a) - 1
            
            if (key < a[mid]) {
                hi = mid - 1;
                reduce_hi_loop_inv(key, a, lo, mid, hi);
            }
            else if (key > a[mid]) {
                lo = mid + 1;
                inc_lo_loop_inv(key, a, lo, mid, hi);
            }
            else
                return mid;

            end_loop_inv(key, a, lo, mid, hi);
        }

        return_fail_inv(lo, hi, key, a);

        return -1;
    }

    private static void passingTests() {
        // passing test cases. Work for all cases where prio < MAXPRIO
        int[] list = {1,2,3,4};
        assert bsearch(list, 3) == 2;
        assert bsearch(list, 2) == 1;
        assert bsearch(list, -2) == -1;
        assert bsearch(list, 4) == 3;


        int[] list2 = {1, 1, 2, 10, 50, 1000};
        assert bsearch(list2, 0) == -1;
        assert bsearch(list2, 51) == -1;
        assert (bsearch(list2, 1) == 0 || bsearch(list2, 1) == 1);
        assert bsearch(list2, 50) == 4;
        assert bsearch(list2, 2) == 2;

        int[] list3 = {-500, 0, 1, 950, Integer.MAX_VALUE};
        assert bsearch(list3, 1) == 2;
        assert bsearch(list3, -1) == -1;
        assert bsearch(list3, 5) == -1;
        assert bsearch(list3, 2) == -1;
        assert bsearch(list3, -500) == 0;
        
        int[] list4 = {2,3,4};
        assert bsearch(list4, 4) == 2;

        int[] list5 = {1, 4, 5, 6};
        assert bsearch(list5, 1) == 0;
        assert bsearch(list5, 4) == 1;
        assert bsearch(list5, 0) == -1;

        // No empty case, because it's "path" is different from othe cases

        int[] list6 = {-1, 0, 1, 1, 2, 4, 8, 11};
        assert bsearch(list6, 8) == 6;
        assert bsearch(list6, 3) == -1;
    }

    private static void failingTests() {
        try {
            int[] list = {20, 32, 53};
            int ind = bsearch(list, 400);
            System.out.println(ind == -1);
        } catch (Exception e) {
            e.printStackTrace();
        }
    }

    public static void main(String[] args) {
        assert args[0].equals("pass") || args[0].equals("both");
        
        passingTests();
        if (args[0].equals("both")) {
            failingTests();
        }
    }
}
