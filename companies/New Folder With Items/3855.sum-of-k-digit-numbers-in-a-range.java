/*
 * @lc app=leetcode id=3855 lang=java
 *
 * [3855] Sum of K-Digit Numbers in a Range
 *
 * Every position independently chooses one number from [l, r]. The sum of all
 * chosen digits over all k-length numbers is arithmeticSum(l..r) *
 * count^(k-1) repeated in every decimal position, hence multiply by the
 * k-digit repunit.
 *
 * Time: O(log k). Space: O(1).
 */

// @lc code=start
class Solution {
    private static final long MOD = 1_000_000_007L;

    public int sumOfNumbers(long l, long r, int k) {
        long count = r - l + 1;
        long digitSum = ((l + r) % MOD) * (count % MOD) % MOD * inv2() % MOD;
        long otherPositions = powMod(count % MOD, k - 1);
        long repunit = (powMod(10, k) - 1 + MOD) % MOD * powMod(9, MOD - 2) % MOD;
        return (int) (digitSum * otherPositions % MOD * repunit % MOD);
    }

    private long inv2() {
        return (MOD + 1) / 2;
    }

    private long powMod(long base, long exp) {
        long result = 1;
        base %= MOD;
        while (exp > 0) {
            if ((exp & 1) == 1) {
                result = result * base % MOD;
            }
            base = base * base % MOD;
            exp >>= 1;
        }
        return result;
    }
}
// @lc code=end
