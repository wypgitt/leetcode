/**
 * Algorithm:
 * Use binary long division by subtracting the largest doubled divisor chunk
 * that fits in the remaining dividend. Work with positive long magnitudes and
 * restore the sign at the end.
 *
 * Java data structures:
 * long is used for intermediate absolute values so Integer.MIN_VALUE can be
 * negated safely.
 *
 * Complexity:
 * Time O(log^2 N) in this doubling form, space O(1).
 */
class Solution {
    public int divide(int dividend, int divisor) {
        if (dividend == Integer.MIN_VALUE && divisor == -1) {
            return Integer.MAX_VALUE;
        }
        boolean negative = (dividend < 0) != (divisor < 0);
        long dividendAbs = Math.abs((long) dividend);
        long divisorAbs = Math.abs((long) divisor);
        long quotient = 0;
        while (dividendAbs >= divisorAbs) {
            long chunk = divisorAbs;
            long multiple = 1;
            while (dividendAbs >= (chunk << 1)) {
                chunk <<= 1;
                multiple <<= 1;
            }
            dividendAbs -= chunk;
            quotient += multiple;
        }
        long signed = negative ? -quotient : quotient;
        return (int) signed;
    }
}
