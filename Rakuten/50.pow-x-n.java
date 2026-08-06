/**
 * Algorithm:
 * Fast exponentiation over the binary representation of n. Square the base each
 * step and multiply it into the answer when the current bit is 1. Negative
 * exponents invert x first.
 *
 * Java data structures:
 * long stores the exponent magnitude so Integer.MIN_VALUE can be negated.
 *
 * Complexity:
 * Time O(log |n|), space O(1).
 */
class Solution {
    public double myPow(double x, int n) {
        long power = n;
        if (power < 0) {
            x = 1.0 / x;
            power = -power;
        }
        double ans = 1.0;
        while (power != 0) {
            if ((power & 1L) == 1L) {
                ans *= x;
            }
            x *= x;
            power >>= 1;
        }
        return ans;
    }
}

