/**
 * Algorithm:
 * DP over prefixes. A one-digit decode is valid for '1'..'9', and a two-digit
 * decode is valid for '10'..'26'. Keep only the previous two prefix counts.
 *
 * Complexity:
 * Time O(n), space O(1).
 */
class Solution {
    public int numDecodings(String s) {
        if (s == null || s.isEmpty() || s.charAt(0) == '0') {
            return 0;
        }
        int twoBack = 1;
        int oneBack = 1;
        for (int i = 1; i < s.length(); i++) {
            int cur = 0;
            if (s.charAt(i) != '0') {
                cur += oneBack;
            }
            int twoDigit = (s.charAt(i - 1) - '0') * 10 + s.charAt(i) - '0';
            if (10 <= twoDigit && twoDigit <= 26) {
                cur += twoBack;
            }
            twoBack = oneBack;
            oneBack = cur;
        }
        return oneBack;
    }
}

