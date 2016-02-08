package src;

import java.util.*;

public class StackArTester
{

    public static boolean scrabbleLettersContainWord(int[] availableLetterCounts,
                                                     String word) {
        int[] wordLetterCounts = new int[availableLetterCounts.length];
        for (char c: word.toCharArray()) {
            wordLetterCounts[(int)c]++;
        }

        for (int i = 0; i < availableLetterCounts.length; i++) {
            if (wordLetterCounts[i] == 0)
                continue;

            // should just be >
            // constraint: all passing inputs have wordLetterCounts[i] > availableLetterCounts[i]
            // failing case would have them ==
            if (wordLetterCounts[i] >= availableLetterCounts[i]) {
                return false;
            }
        }

        return true;
    }

    public static void main(String[] args) {
        int[] letterCounts = new int[256];

        letterCounts[(int)'a'] = 5;
        letterCounts[(int)'p'] = 3;
        letterCounts[(int)'l'] = 2;
        letterCounts[(int)'e'] = 2;

        System.out.println(scrabbleLettersContainWord(letterCounts, "apple"));
    }

}
