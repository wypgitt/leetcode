/**
 * Algorithm:
 * Character i is affected by shifts[i] through shifts[n - 1]. Scan from right
 * to left, maintain the suffix sum modulo 26, and shift each character once.
 *
 * Complexity:
 * Time O(n), space O(n) for the output character array.
 */
class Solution {
    public String shiftingLetters(String s, int[] shifts) {
        char[] chars = s.toCharArray();
        int total = 0;
        for (int i = s.length() - 1; i >= 0; i--) {
            total = (int) ((total + (long) shifts[i]) % 26);
            chars[i] = (char) ((chars[i] - 'a' + total) % 26 + 'a');
        }
        return new String(chars);
    }
}

