/**
 * Algorithm:
 * Reverse the absolute value digit by digit, restore the sign, and reject the
 * result if it falls outside the signed 32-bit integer range.
 *
 * Java data structures:
 * long stores the intermediate reversed value so overflow can be detected
 * safely before casting to int.
 *
 * Complexity:
 * Time O(log10 |x|), space O(1).
 */
class Solution {
    public int reverse(int x) {
        int sign = x < 0 ? -1 : 1;
        long num = Math.abs((long) x);
        long ans = 0;
        while (num != 0) {
            ans = ans * 10 + num % 10;
            num /= 10;
        }
        ans *= sign;
        return ans < Integer.MIN_VALUE || ans > Integer.MAX_VALUE ? 0 : (int) ans;
    }
}

