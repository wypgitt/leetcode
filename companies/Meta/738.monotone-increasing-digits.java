/**
 * Algorithm:
 * Scan digits right to left. When a digit is greater than the digit after it,
 * decrement it and mark every later position to become 9. This creates the
 * largest valid number not exceeding n.
 *
 * Complexity:
 * Time O(d), space O(d), where d is the digit count.
 */
class Solution {
    public int monotoneIncreasingDigits(int n) {
        char[] digits = String.valueOf(n).toCharArray();
        int marker = digits.length;
        for (int i = digits.length - 1; i > 0; i--) {
            if (digits[i - 1] > digits[i]) {
                digits[i - 1]--;
                marker = i;
            }
        }
        for (int i = marker; i < digits.length; i++) {
            digits[i] = '9';
        }
        return Integer.parseInt(new String(digits));
    }
}

