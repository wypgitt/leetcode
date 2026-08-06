/*
 * @lc app=leetcode id=793 lang=java
 *
 * [793] Preimage Size of Factorial Zeroes Function
 *
 * Z(n) = trailing zeros in n!. Monotone; answer is 0 or 5. Binary search first n with Z(n) >= k.
 */

// @lc code=start
class Solution {
    public int preimageSizeFZF(int k) {
        long lo = 0;
        long hi = 5L * (k + 1);
        while (lo < hi) {
            long mid = (lo + hi) >>> 1;
            if (trailingZerosFactorial(mid) < k) {
                lo = mid + 1;
            } else {
                hi = mid;
            }
        }
        return trailingZerosFactorial(lo) == k ? 5 : 0;
    }

    private long trailingZerosFactorial(long n) {
        long z = 0;
        while (n > 0) {
            n /= 5;
            z += n;
        }
        return z;
    }
}
// @lc code=end
