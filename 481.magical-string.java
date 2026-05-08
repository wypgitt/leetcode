/*
 * @lc app=leetcode id=481 lang=java
 *
 * [481] Magical String
 *
 * Generate the magical string from its run-length description. read points to
 * the next run length, nextValue alternates between 1 and 2, and we count ones
 * only while appended positions are within the first n values.
 *
 * Time: O(n). Space: O(n).
 */

import java.util.ArrayList;
import java.util.List;

// @lc code=start
class Solution {
    public int magicalString(int n) {
        if (n <= 3) {
            return 1;
        }

        List<Integer> magical = new ArrayList<>();
        magical.add(1);
        magical.add(2);
        magical.add(2);
        int read = 2;
        int nextValue = 1;
        int ones = 1;

        while (magical.size() < n) {
            int repeat = magical.get(read);
            for (int i = 0; i < repeat; i++) {
                magical.add(nextValue);
                if (nextValue == 1 && magical.size() <= n) {
                    ones++;
                }
            }
            nextValue = 3 - nextValue;
            read++;
        }
        return ones;
    }
}
// @lc code=end
