/*
 * @lc app=leetcode id=522 lang=java
 *
 * [522] Longest Uncommon Subsequence II
 *
 * Test candidate strings from longest to shortest. A candidate is uncommon if
 * it is not a subsequence of any other string with length at least as large.
 * The first such candidate has maximum length.
 *
 * Time: O(n^2 * L). Space: O(n).
 */

import java.util.Arrays;

// @lc code=start
class Solution {
    public int findLUSlength(String[] strs) {
        Integer[] order = new Integer[strs.length];
        for (int i = 0; i < strs.length; i++) {
            order[i] = i;
        }
        Arrays.sort(order, (a, b) -> Integer.compare(strs[b].length(), strs[a].length()));

        for (int index : order) {
            String candidate = strs[index];
            boolean uncommon = true;
            for (int other = 0; other < strs.length; other++) {
                if (other == index) {
                    continue;
                }
                if (strs[other].length() >= candidate.length() && isSubsequence(candidate, strs[other])) {
                    uncommon = false;
                    break;
                }
            }
            if (uncommon) {
                return candidate.length();
            }
        }
        return -1;
    }

    private boolean isSubsequence(String small, String large) {
        int pointer = 0;
        for (int i = 0; i < large.length() && pointer < small.length(); i++) {
            if (small.charAt(pointer) == large.charAt(i)) {
                pointer++;
            }
        }
        return pointer == small.length();
    }
}
// @lc code=end
