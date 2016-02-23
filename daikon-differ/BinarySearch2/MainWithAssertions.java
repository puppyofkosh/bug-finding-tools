import daikon.Quant;

public class MainWithAssertions {

    private static void start_loop_inv(int key, int a[], int lo, int mid, int hi) {
        assert         a != null;
        assert daikon.Quant.eltwiseLTE(a);
        assert lo >= 0;
        assert mid >= 0;
        assert lo <= mid;
        assert lo <= hi;
        assert lo <= daikon.Quant.size(a)-1;
        assert mid <= hi;
        assert mid <= daikon.Quant.size(a)-1;
        assert hi <= daikon.Quant.size(a);
        assert hi != daikon.Quant.size(a)-1;
        assert daikon.Quant.getElement_int(a, lo) <= daikon.Quant.getElement_int(a, mid);
    }
    private static void end_loop_inv(int key, int a[], int lo, int mid, int hi) {
        assert a != null;
        assert daikon.Quant.eltwiseLTE(a);
        assert lo >= 0;
        assert mid >= 0;
        assert hi >= -1;
        assert key != daikon.Quant.size(a)-1;
        assert key != daikon.Quant.getElement_int(a, mid);
        assert lo <= daikon.Quant.size(a)-1;
        assert mid <= daikon.Quant.size(a)-1;
        assert hi <= daikon.Quant.size(a);
        assert hi != daikon.Quant.size(a)-1;
        assert daikon.Quant.size(a)-1 != daikon.Quant.getElement_int(a, lo);
    }

    private static void reduce_hi_loop_inv(int key, int a[], int lo, int mid, int hi) {
        assert         a != null;
        assert daikon.Quant.eltwiseLTE(a);
        assert lo >= 0;
        assert mid >= 0;
        assert hi >= -1;
        assert key != daikon.Quant.size(a)-1;
        assert key < daikon.Quant.getElement_int(a, mid);
        assert lo <= mid;
        assert lo < daikon.Quant.size(a)-1;
        assert lo != daikon.Quant.getElement_int(a, lo);
        assert lo != daikon.Quant.getElement_int(a, mid);
        assert mid - hi - 1 == 0;
        assert mid <= daikon.Quant.size(a)-1;
        assert hi < daikon.Quant.size(a)-1;
        assert hi <= daikon.Quant.getElement_int(a, mid);
        assert daikon.Quant.size(a) != daikon.Quant.getElement_int(a, lo);
        assert daikon.Quant.size(a)-1 != daikon.Quant.getElement_int(a, lo);
        assert daikon.Quant.getElement_int(a, lo) <= daikon.Quant.getElement_int(a, mid);
    }


    private static void inc_lo_loop_inv(int key, int a[], int lo, int mid, int hi) {
        assert daikon.Quant.getElement_int(a, lo-1) == daikon.Quant.getElement_int(a, mid);
        assert a != null;
        assert daikon.Quant.eltwiseLTE(a);
        assert lo >= 1;
        assert mid >= 0;
        assert hi >= 1;
        assert key != daikon.Quant.size(a)-1;
        assert key > daikon.Quant.getElement_int(a, mid);
        assert lo - mid - 1 == 0;
        assert lo <= daikon.Quant.size(a)-1;
        assert mid <= hi;
        assert mid < daikon.Quant.size(a)-1;
        assert mid <= daikon.Quant.getElement_int(a, lo);
        assert hi <= daikon.Quant.size(a);
        assert hi != daikon.Quant.size(a)-1;
        assert daikon.Quant.size(a)-1 != daikon.Quant.getElement_int(a, lo);
        assert daikon.Quant.size(a)-1 != daikon.Quant.getElement_int(a, hi-1);
        assert daikon.Quant.getElement_int(a, lo) > daikon.Quant.getElement_int(a, mid);
    }

    private static void return_fail_inv(int l, int h, int k, int[] arr) {
        assert         l >= 0;
        assert daikon.Quant.eltwiseLTE(arr);
        assert l - h - 1 == 0;
        assert l <= daikon.Quant.size(arr)-1;
        assert l != daikon.Quant.getElement_int(arr, l);
        assert h < daikon.Quant.size(arr)-1;
        assert h <= daikon.Quant.getElement_int(arr, l);
        assert k != daikon.Quant.size(arr)-1;
        assert k < daikon.Quant.getElement_int(arr, l);
        assert daikon.Quant.size(arr) != daikon.Quant.getElement_int(arr, l);
        assert daikon.Quant.size(arr)-1 != daikon.Quant.getElement_int(arr, l);
    }

    public static int bsearch(int[] a, int key) {
        final int old_key = key;
        int lo = 0;
        // should be a.length - 1
        int hi = a.length;
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
            else {
                assert key == a[mid];
                return mid;
            }

            end_loop_inv(key, a, lo, mid, hi);
        }

        return_fail_inv(lo, hi, key, a);

        assert old_key != daikon.Quant.size(a)-1;
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
