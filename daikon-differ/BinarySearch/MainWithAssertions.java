import daikon.Quant;

public class MainWithAssertions {

    private static void dummy_fn(int key, int elem, int l, int m, int h) {
        assert l >= 0;
        assert m >= 0;
        assert l <= m;
        assert l < h;
        assert m < h;
    }
    private static void dummy_fn_reduce_hi(int key, int elem, int l, int m, int h) {
        // Bad constraints, but we keep em here for now
        assert elem == 1 || elem == 2 || elem == 950;
        assert l == 0 || l == 3;
        //
        assert key < elem;
        assert elem > l;
        assert elem >= h;
        assert l <= m;
        assert m - h - 1 == 0;
    }
    private static void dummy_fn_inc_lo(int key, int elem, int l, int m, int h) {
        assert key > elem;
        assert key != l;
        assert l - m - 1 == 0;
        assert l <= h;
        assert m < h;
    }

    private static void dummy_fn2(int l, int h, int k, int[] arr) {
        assert l >= h;
        assert l <= daikon.Quant.size(arr)-1;
        assert l != daikon.Quant.getElement_int(arr, l);
        assert h <= daikon.Quant.size(arr)-1;
        assert h != daikon.Quant.getElement_int(arr, l);
        assert k != daikon.Quant.size(arr)-1;
        // This is the invariant that fails the failing case
        assert k != daikon.Quant.getElement_int(arr, l);
        //
        assert daikon.Quant.size(arr)-1 != daikon.Quant.getElement_int(arr, l);
    }

    private static void before_loop(int l, int h, int k, int[] arr) {
        assert h == daikon.Quant.size(arr)-1;
        assert l == 0;
        assert arr != null;
        assert daikon.Quant.eltwiseLTE(arr);
        assert daikon.Quant.getElement_int(arr, l) == -500 || daikon.Quant.getElement_int(arr, l) == -1 || daikon.Quant.getElement_int(arr, l) == 1;
        assert l < h;
        assert l != daikon.Quant.getElement_int(arr, l);
        assert l < daikon.Quant.getElement_int(arr, h);
        assert l < daikon.Quant.getElement_int(arr, h-1);
        assert h > daikon.Quant.getElement_int(arr, l);
        assert h <= daikon.Quant.getElement_int(arr, h-1);
        assert k != daikon.Quant.getElement_int(arr, h);
        assert daikon.Quant.eltsGTE(arr, daikon.Quant.getElement_int(arr, l));
        assert daikon.Quant.eltsLTE(arr, daikon.Quant.getElement_int(arr, h));
        assert daikon.Quant.size(arr) <= daikon.Quant.getElement_int(arr, h);
        assert daikon.Quant.getElement_int(arr, l) < daikon.Quant.getElement_int(arr, h);
        assert daikon.Quant.getElement_int(arr, l) < daikon.Quant.getElement_int(arr, h-1);
        assert daikon.Quant.getElement_int(arr, h) > daikon.Quant.getElement_int(arr, h-1);
    }


    public static int bsearch(int[] a, int key) {
        final int orig_key = key;

        assert a != null;
        assert daikon.Quant.eltwiseLTE(a);

        int lo = 0;
        int hi = a.length - 1;
        // should be <=
        while (lo < hi) {
            int mid = lo + (hi - lo) / 2;

            // forces daikon to compute invariants about dummy_fn input and output,
            // which are in this case, loop invariants.
            dummy_fn(key, a[mid], lo, mid, hi);

            if (key < a[mid]) {
                hi = mid - 1;
                dummy_fn_reduce_hi(key, a[mid], lo, mid, hi);
            }
            else if (key > a[mid]) {
                lo = mid + 1;
                dummy_fn_inc_lo(key, a[mid], lo, mid, hi);
            }
            else {
                return mid;
            }

        }

        // constraint:
        // low >= hi
        // a[low] != key
        //assert a.length == 0 || a[lo] != key;
        dummy_fn2(lo, hi, key, a);

        return -1;
    }

    private static void passingTests() {
        // passing test cases. Work for all cases where prio < MAXPRIO
        int[] list = {1,2,3,4};
        assert bsearch(list, 3) == 2;
        assert bsearch(list, 2) == 1;
        assert bsearch(list, 5) == -1;
        assert bsearch(list, -2) == -1;

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

        //int[] list4 = {};
        //assert bsearch(list4, 0) == -1;

        int[] list6 = {-1, 0, 1, 1, 2, 4, 8, 11};
        assert bsearch(list6, 8) == 6;
        assert bsearch(list6, 12) == -1;
    }

    private static void failingTests() {
        int[] list = {1,2,3,4};
        int ind = bsearch(list, 1);
        System.out.println(ind == 0);
    }

    public static void main(String[] args) {
        assert args[0].equals("pass") || args[0].equals("both");
        
        passingTests();
        if (args[0].equals("both")) {
            failingTests();
        }
    }
}
