public class MainWithAssertions {

    public static void start_inv(String s, String p) {
        assert s != null;
        assert p != null;
        assert s.toString().length() >= 0;
        assert p.toString().length() >= 0;
    }

    public static void not_star_inv(String s, String p) {
        assert s != null;
        assert p != null;
        assert s.toString().length() >= 1;
        assert p.toString().length() >= 1;
    }

    public static void not_star_ret_false_inv(String s, String p) {
        assert !s.toString().equals(p.toString());
        assert s.toString().length() >= p.toString().length();
    }
    public static void not_star_recur_inv(String s, String p) {
        assert s != null;
        assert p != null;
        assert s.toString().length() >= 1;
        assert p.toString().length() >= 1;
    }

    public static void is_star_loop_inv(String s, String p, int i, int len) {
        assert len == s.toString().length();
        assert s != null;
        assert p != null;
        assert i >= -1;
        assert !s.toString().equals(p.toString());
        assert i < len;
    }
    public static void ret_true_inv(String s, String p, int i, int len) {
        assert len == s.toString().length();
        assert i >= -1;
        assert !s.toString().equals(p.toString());
        assert i < len;
        assert i - len + p.toString().length() - 1 == 0;
    }

    public static void loop_exit_inv(String s, String p, int i, int len) {
        // No invariants generated
    }

    public static boolean isMatch(String s, String p) {
        start_inv(s,p);
        if(p.length() == 0)
            return s.length() == 0;
 
        if(p.length() == 1 || p.charAt(1) != '*'){
            not_star_inv(s,p);
            if(/*s.length() < 1 || */(p.charAt(0) != '.' && s.charAt(0) != p.charAt(0))) {
                not_star_ret_false_inv(s,p);
                return false;
            }
            not_star_recur_inv(s,p);
            return isMatch(s.substring(1), p.substring(1));    
 
        } else{
            assert p.charAt(1) == '*';

            int len = s.length();
            int i = -1; 
            while(i<len && (i < 0 || p.charAt(0) == '.' || p.charAt(0) == s.charAt(i))){
                is_star_loop_inv(s, p, i, len);

                if(isMatch(s.substring(i+1), p.substring(2))) {
                    ret_true_inv(s, p, i, len);
                    return true;
                }
                i++;
            }
            loop_exit_inv(s, p, i, len);
            return false;
        } 
    }

    private static void passingTests() {
        assert isMatch("aa","a") == false;
        assert isMatch("aa","aa") == true;
        assert isMatch("aaa","aa") == false;

        assert isMatch("aaa", ".*") == true;
        assert isMatch("aaaaaaa", ".*") == true;
        assert isMatch("ab", ".*") == true;
        assert isMatch("aa", "aa.*") == true;
        assert isMatch("abcaa", "a.*aa") == true;
        assert isMatch("aaa", "a.*aa") == true;
        assert isMatch("a", "a*") == true;
        assert isMatch("aa", "a*") == true;
        assert isMatch("aab", "c*a*b") == true;

        assert isMatch("qabqw", "qaq.*") == false;
        assert isMatch("Loooooo", "Doo.*") == false;
        assert isMatch("wxyz", ".*xyz") == true;

    }

    private static void failingTests() {
        assert isMatch("ab", "abc") == false;
    }


    public static void main(String[] args) {
        passingTests();

        if (args[0].equals("both")) {
            try {
                failingTests();
            } catch (Exception e) {
                e.printStackTrace();
            }
        }
    }
}
