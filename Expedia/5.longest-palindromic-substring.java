/**
 * Algorithm:
 * Expand around every possible odd and even center. Each expansion stops at a
 * mismatch or boundary, and the best range is tracked.
 *
 * Complexity:
 * Time O(n^2), space O(1).
 */
class Solution {
    public String longestPalindrome(String s) {
        int bestLeft = 0;
        int bestRight = 0;
        for (int i = 0; i < s.length(); i++) {
            int[] odd = expand(s, i, i);
            if (odd[1] - odd[0] > bestRight - bestLeft) {
                bestLeft = odd[0];
                bestRight = odd[1];
            }
            int[] even = expand(s, i, i + 1);
            if (even[1] - even[0] > bestRight - bestLeft) {
                bestLeft = even[0];
                bestRight = even[1];
            }
        }
        return s.substring(bestLeft, bestRight + 1);
    }

    private int[] expand(String s, int left, int right) {
        while (left >= 0 && right < s.length() && s.charAt(left) == s.charAt(right)) {
            left--;
            right++;
        }
        return new int[] {left + 1, right - 1};
    }
}

