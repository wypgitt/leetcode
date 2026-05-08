/*
 * @lc app=leetcode id=3881 lang=java
 *
 * [3881] Direction Assignments With Exactly K Visible People
 *
 * The Python solution reduces the count to 2 * C(n - 1, k). Precompute
 * factorials and inverse factorials modulo 1e9+7, then evaluate the binomial.
 *
 * Java note: modular inverses use fast exponentiation by MOD - 2.
 *
 * Time: O(n + log MOD). Space: O(n).
 */

// @lc code=start
class Solution {
    private static final long MOD = 1_000_000_007L;

    public int countVisiblePeople(int n, int pos, int k) {
        int total = n - 1;
        if (k > total) {
            return 0;
        }

        long[] factorial = new long[total + 1];
        long[] inverseFactorial = new long[total + 1];
        factorial[0] = 1;
        for (int i = 1; i <= total; i++) {
            factorial[i] = factorial[i - 1] * i % MOD;
        }
        inverseFactorial[total] = pow(factorial[total], MOD - 2);
        for (int i = total; i > 0; i--) {
            inverseFactorial[i - 1] = inverseFactorial[i] * i % MOD;
        }

        long combinations = factorial[total] * inverseFactorial[k] % MOD * inverseFactorial[total - k] % MOD;
        return (int) (2 * combinations % MOD);
    }

    private long pow(long base, long exp) {
        long result = 1;
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
