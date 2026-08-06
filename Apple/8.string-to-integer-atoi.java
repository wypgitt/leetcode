/**
 * Algorithm:
 * Parse the fixed grammar: leading spaces, optional sign, then consecutive
 * digits. Clamp during accumulation to the signed 32-bit range.
 *
 * Java data structures:
 * long stores the partial value during parsing so overflow can be detected
 * before converting to int.
 *
 * Complexity:
 * Time O(n) in the parsed prefix, space O(1).
 */
class Solution {
    public int myAtoi(String s) {
        int i = 0;
        int n = s.length();
        while (i < n && s.charAt(i) == ' ') {
            i++;
        }
        int sign = 1;
        if (i < n && (s.charAt(i) == '+' || s.charAt(i) == '-')) {
            sign = s.charAt(i) == '-' ? -1 : 1;
            i++;
        }
        long value = 0;
        while (i < n && Character.isDigit(s.charAt(i))) {
            value = value * 10 + s.charAt(i) - '0';
            if (sign == 1 && value >= Integer.MAX_VALUE) {
                return Integer.MAX_VALUE;
            }
            if (sign == -1 && -value <= Integer.MIN_VALUE) {
                return Integer.MIN_VALUE;
            }
            i++;
        }
        return (int) (sign * value);
    }
}

