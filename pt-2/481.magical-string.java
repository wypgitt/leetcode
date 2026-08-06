import java.util.*;

/**
 * Algorithm:
 * Build the magical string while a read pointer tells how many copies of the
 * next number to append. The next number alternates between 1 and 2.
 *
 * Java data structures:
 * ArrayList<Integer> gives append and indexed read access like the Python list.
 *
 * Complexity:
 * Time O(n), space O(n).
 */
class Solution {
    public int magicalString(int n) {
        if (n <= 0) {
            return 0;
        }
        List<Integer> s = new ArrayList<>();
        s.add(1);
        s.add(2);
        s.add(2);
        if (n <= 3) {
            int count = 0;
            for (int i = 0; i < n; i++) {
                if (s.get(i) == 1) {
                    count++;
                }
            }
            return count;
        }

        int read = 2;
        int nextNum = 1;
        int ones = 1;
        while (s.size() < n) {
            int repeat = s.get(read);
            for (int i = 0; i < repeat && s.size() < n; i++) {
                s.add(nextNum);
                if (nextNum == 1) {
                    ones++;
                }
            }
            nextNum = 3 - nextNum;
            read++;
        }
        return ones;
    }
}

