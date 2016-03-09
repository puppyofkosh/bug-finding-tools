import java.io.IOException;
import java.io.InputStreamReader;
import java.io.Reader;
import java.util.Arrays;
import java.util.Scanner;

/**
 * Created by puppyofkosh on 3/8/16.
 */
public class Main {

    /*  -*- Last-Edit:  Mon Dec  7 10:31:51 1992 by Tarak S. Goradia; -*- */

    private static final int MAXSTR = 100;
    private static final int MAXPAT = MAXSTR;

    private static final char ENDSTR = '\0';
    private static final char ESCAPE = '@';
    private static final char CLOSURE ='*';
    private static final char BOL    = '%';
    private static final char EOL    = '$';
    private static final char ANY    = '?';
    private static final char CCL    = '[';
    private static final char CCLEND = ']';
    private static final char NEGATE = '^';
    private static final char NCCL   = '!';
    private static final char LITCHAR ='c';
    private static final char DITTO  = (char)(-1);
    private static final char DASH   = '-';

    private static char TAB   =  9;
    private static char NEWLINE =10;

    private static int CLOSIZE= 1;

    public static int
    addstr(char c, char[] outset, int[] j, int maxset)
    {
        boolean	result;
        if (j[0] >= maxset)
            result = false;
        else {
            outset[j[0]] = c;
            j[0] = j[0] + 1;
            result = true;
        }
        return result ? 1 : 0;
    }
    //
    public static char
    esc(char[] s, int[] i)
    {
        char	result;
        if (s[i[0]] != ESCAPE)
            result = s[i[0]];
        else {
            if (s[i[0] + 1] == ENDSTR)
                result = ESCAPE;
            else {
                i[0] = i[0] + 1;
                if (s[i[0]] == 'n')
                    result = NEWLINE;
                else if (s[i[0]] == 't')
                    result = TAB;
                else
                    result = s[i[0]];
            }
        }
        return result;
    }

    public static boolean isalnum(char c) {
        return Character.isAlphabetic(c) || Character.isDigit(c);
    }

    public static void
    dodash(char delim, char[] src, int[] i, char[] dest, int[] j, int maxset)
    {
        int	k;
        boolean	junk;
        char	escjunk;

        while ((src[i[0]] != delim) && (src[i[0]] != ENDSTR))
        {
            if (src[i[0] - 1] == ESCAPE) {
                escjunk = esc(src, i);
                junk = addstr(escjunk, dest, j, maxset) != 0;
            } else {
                if (src[i[0]] != DASH)
                    junk = addstr(src[i[0]], dest, j, maxset) != 0;
                else if (j[0] <= 1 || src[i[0] + 1] == ENDSTR)
                    junk = addstr(DASH, dest, j, maxset) != 0;
                else if ((isalnum(src[i[0] - 1])) && (isalnum(src[i[0] + 1]))
                        && (src[i[0] - 1] <= src[i[0] + 1])) {
                    for (k = src[i[0] - 1] + 1; k <= src[i[0] + 1]; k++) {
                        junk = addstr((char)k, dest, j, maxset) != 0;
                    }
                    i[0] = i[0] + 1;
                } else
                    junk = addstr(DASH, dest, j, maxset) != 0;
            }
            (i[0]) = (i[0]) + 1;
        }
    }

    public static boolean
    getccl(char[] arg, int[] i, char[] pat, int[] j)
    {
        int	jstart;
        boolean	junk;

        i[0] = i[0] + 1;
        if (arg[i[0]] == NEGATE) {
            junk = addstr(NCCL, pat, j, MAXPAT) != 0;
            i[0] = i[0] + 1;
        } else
            junk = addstr(CCL, pat, j, MAXPAT) != 0;
        jstart = j[0];
        junk = addstr((char)0, pat, j, MAXPAT) != 0;
        dodash(CCLEND, arg, i, pat, j, MAXPAT);
        pat[jstart] = (char)(j[0] - jstart - 1);
        return (arg[i[0]] == CCLEND);
    }

    public static void
    stclose(char[] pat, int[] j, int lastj)
    {
        int	jt;
        int	jp;
        boolean	junk;


        for (jp = j[0] - 1; jp >= lastj ; jp--)
        {
            jt = jp + CLOSIZE;

            int[] jt_ptr = {jt};
            junk = addstr(pat[jp], pat, jt_ptr, MAXPAT) != 0;
            jt = jt_ptr[0];
        }
        j[0] = j[0] + CLOSIZE;
        pat[lastj] = CLOSURE;
    }

    public static boolean in_set_2(char c)
    {
        return (c == BOL || c == EOL || c == CLOSURE);
    }

    public static boolean in_pat_set(char c)
    {
        return (   c == LITCHAR || c == BOL  || c == EOL || c == ANY
                || c == CCL     || c == NCCL || c == CLOSURE);
    }
    //
    public static int
    makepat(char[] arg, int start, char delim, char[] pat)
    {
        int	result;
        int	i, j, lastj, lj;
        boolean	done, junk;
        boolean	getres;
        char	escjunk;

        j = 0;
        i = start;
        lastj = 0;
        done = false;
        while ((!done) && (arg[i] != delim) && (arg[i] != ENDSTR)) {
            lj = j;

            if ((arg[i] == ANY)) {
                int[] j_ptr = {j};
                junk = addstr(ANY, pat, j_ptr, MAXPAT) != 0;
                j = j_ptr[0];
            }
            else if ((arg[i] == BOL) && (i == start)) {
                int[] j_ptr = {j};
                junk = addstr(BOL, pat, j_ptr, MAXPAT) != 0;
                j = j_ptr[0];

            }
            else if ((arg[i] == EOL) && (arg[i+1] == delim)) {
                int[] j_ptr = {j};
                junk = addstr(EOL, pat, j_ptr, MAXPAT) != 0;
                j = j_ptr[0];

            }
            else if ((arg[i] == CCL))
            {
                int[] j_ptr = {j};
                int[] i_ptr = {i};
                getres = getccl(arg, i_ptr, pat, j_ptr);
                i = i_ptr[0];
                j = j_ptr[0];

                done = (boolean)(getres == false);
            }
            else if ((arg[i] == CLOSURE) && (i > start))
            {
                lj = lastj;
                if (in_set_2(pat[lj]))
                    done = true;
                else {
                    int[] j_ptr = {j};
                    stclose(pat, j_ptr, lastj);
                    j = j_ptr[0];
                }
            }
            else
            {
                int[] j_ptr = {j};
                junk = addstr(LITCHAR, pat, j_ptr, MAXPAT) != 0;
                j = j_ptr[0];

                int[] i_ptr = {i};
                escjunk = esc(arg, i_ptr);
                i = i_ptr[0];

                j_ptr[0] = j;
                junk = addstr(escjunk, pat, j_ptr, MAXPAT) != 0;
                j = j_ptr[0];
            }
            lastj = lj;
            if ((!done))
                i = i + 1;
        }

        int[] j_ptr = {j};
        junk = addstr(ENDSTR, pat, j_ptr, MAXPAT) != 0;
        j = j_ptr[0];

        if ((done) || (arg[i] != delim))
            result = 0;
        else
        if ((!junk))
            result = 0;
        else
            result = i;
        return result;
    }

    public static int
    getpat(char[] arg, char[] pat)
    {
        int	makeres;

        makeres = makepat(arg, 0, ENDSTR, pat);
        return (makeres > 0) ? 1 : 0;
    }

    public static int
    makesub(char[] arg, int from, char delim, char[] sub)
    {
        int  result;
        int	i, j;
        boolean	junk;
        char	escjunk;

        j = 0;
        i = from;
        while ((arg[i] != delim) && (arg[i] != ENDSTR)) {
            if ((arg[i] == ('&'))) {
                int[] j_ptr = {j};
                junk = addstr(DITTO, sub, j_ptr, MAXPAT) != 0;
                j = j_ptr[0];
            }
            else {
                int[] i_ptr = {i};
                escjunk = esc(arg, i_ptr);
                i = i_ptr[0];

                int[] j_ptr = {j};
                junk = addstr(escjunk, sub, j_ptr, MAXPAT) != 0;
                j = j_ptr[0];
            }
            i = i + 1;
        }
        if (arg[i] != delim)
            result = 0;
        else {
            //junk = addstr(ENDSTR, &(*sub), &j, MAXPAT);
            int[] j_ptr = {j};
            junk = addstr(ENDSTR, sub, j_ptr, MAXPAT) != 0;
            j = j_ptr[0];
            if ((!junk))
                result = 0;
            else
                result = i;
        }
        return result;
    }

    public static boolean
    getsub(char[] arg, char[] sub)
    {
        int	makeres;

        makeres = makesub(arg, 0, ENDSTR, sub);
        return (makeres > 0);
    }


    public static boolean
    locate(char c, char[] pat, int offset)
    {
        int	i;
        boolean flag;

        flag = false;
        i = offset + pat[offset];
        while ((i > offset))
        {
            if (c == pat[i]) {
                flag = true;
                i = offset;
            } else
                i = i - 1;
        }
        return flag;
    }
//

    public static boolean
    omatch(char[] lin, int[] i, char[] pat, int j)
    {
        int	advance;
        boolean result;

        advance = -1;
        if ((lin[i[0]] == ENDSTR))
            result = false;
        else
        {
            if (!in_pat_set(pat[j]))
            {
                System.out.println("in omatch: can't happen\n");
                System.exit(1);
            } else
            {
                switch (pat[j])
                {
                    case LITCHAR:
                        if (lin[i[0]] == pat[j + 1])
                            advance = 1;
                        break ;
                    case BOL:
                        if (i[0] == 0)
                            advance = 0;
                        break ;
                    case ANY:
                        if (lin[i[0]] != NEWLINE)
                            advance = 1;
                        break ;
                    case EOL:
                        if (lin[i[0]] == NEWLINE)
                            advance = 0;
                        break ;
                    case CCL:
                        if (locate(lin[i[0]], pat, j + 1))
                            advance = 1;
                        break ;
                    case NCCL:
                        if ((lin[i[0]] != NEWLINE) && (!locate(lin[i[0]], pat, j+1)))
                            advance = 1;
                        break ;
                    default:
                        Caseerror(pat[j]);
                };
            }
        }
        if ((advance >= 0))
        {
            i[0] = i[0] + advance;
            result = true;
        } else
            result = false;
        return result;
    }
    //
//
    public static int
    patsize(char[] pat, int n)
    {
        int size=-1;
        if (!in_pat_set(pat[n])) {
            System.out.print("in patsize: can't happen\n");
            System.exit(1);
        } else
            switch (pat[n])
            {
                case LITCHAR: size = 2; break;

                case BOL:  case EOL:  case ANY:
                size = 1;
                break;
                case CCL:  case NCCL:
                size = pat[n + 1] + 2;
                break ;
                case CLOSURE:
                    size = CLOSIZE;
                    break ;
                default:
                    Caseerror(pat[n]);
            }
        return size;
    }
    //
    public static int
    amatch(char[] lin, int offset, char[] pat, int j)
    {
        int	i=-1, k=-1;
        boolean	result, done;

        done = false;
        while ((!done) && (pat[j] != ENDSTR))
            if ((pat[j] == CLOSURE)) {
                j = j + patsize(pat, j);
                i = offset;
                while ((!done) && (lin[i] != ENDSTR)) {
                    int[] mutable_i = {i};
                    result = omatch(lin, mutable_i, pat, j);
                    i = mutable_i[0];
                    if (!result)
                        done = true;
                }
                done = false;
                while ((!done) && (i >= offset)) {
                    k = amatch(lin, i, pat, j + patsize(pat, j));
                    if ((k >= 0))
                        done = true;
                    else
                        i = i - 1;
                }
                offset = k;
                done = true;
            } else {
                int[] mutable_offset = {offset};
                result = omatch(lin, mutable_offset, pat, j);
                offset = mutable_offset[0];
                if ((!result)) {
                    offset = -1;
                    done = true;
                } else
                    j = j + patsize(pat, j);
            }
        return offset;
    }

    public static void
    putsub(char[] lin, int s1, int s2, char[] sub)
    {
        int	i;
        int	j;

        i = 0;
        while ((sub[i] != ENDSTR)) {
            if ((sub[i] == DITTO))
                for (j = s1; j < s2; j++)
                {
                    System.out.print(lin[j]);
                    //fputc(lin[j],stdout);
                }
            else
            {
                System.out.print(sub[i]);
                //fputc(sub[i],stdout);
            }
            i = i + 1;
        }
    }

    public static void
    subline(char[] lin, char[] pat, char[] sub)
    {
        int	i, lastm, m;

        lastm = -1;
        i = 0;
        while ((lin[i] != ENDSTR))
        {
            m = amatch(lin, i, pat, 0);
            if ((m >= 0) && (lastm != m)) {
                putsub(lin, i, m, sub);
                lastm = m;
            }
            if ((m == -1) || (m == i)) {
                System.out.print(lin[i]);
                //fputc(lin[i],stdout);
                i = i + 1;
            } else
                i = m;
        }
    }

    public static void change(char[] pat, char[] sub) {
        //Scanner in = new Scanner(System.in);//stdin
        Reader reader = new InputStreamReader(System.in);

        while(true) {
            int c = -1;
            String line = new String();
            while (true) {
                try {
                    c = reader.read();
                } catch(IOException e) {
                    e.printStackTrace();
                }

                if (c != -1)
                    line += (char)c;

                if (c == -1 || c == '\n')
                    break;

                // Original tool uses fgets, which reads one character less
                // than given arg
                if (line.length() == MAXSTR - 1)
                    break;
            }

            char[] l = Arrays.copyOf(line.toCharArray(), line.length() + 1);
            subline(l, pat, sub);

            if (c == -1)
                break;
        }
    }


    public static void main(String[] args) {

        // need to include space for null terminator
        // Also, the C programs sometimes rely on undefined behavior (reading off the end of the array)
        // so we include extra padded space at the end
        char []pat = new char[MAXSTR + 100];
        char []sub = new char[MAXSTR + 100];
        //char []pat = new char[MAXSTR];
        //char []sub = new char[MAXSTR];
        boolean result;



        if (args.length < 1)
        {
            System.out.println("usage: change from [to]");
            return;
        }
        char[] arg0 = Arrays.copyOf(args[0].toCharArray(), args[0].length() + 1);

        result = getpat(arg0, pat) != 0;
        if (!result)
        {
            System.out.println("change: illegal \"from\" pattern");
            return;
        }

        if (args.length >= 2)
        {
            char[] arg1 = Arrays.copyOf(args[1].toCharArray(), args[1].length() + 1);
            result = getsub(arg1, sub);
            if (!result)
            {
                System.out.println("change: illegal \"to\" string");
                return;
            }
        } else
        {
            sub[0] = '\0';
        }

        change(pat, sub);
        //return 0;
    }

    public static void
    Caseerror(int n)
    {
        System.out.print("Missing case limb: line " + n);
        System.exit(4);
    }
}