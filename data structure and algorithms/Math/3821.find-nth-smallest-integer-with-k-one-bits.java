/*
 * @lc app=leetcode id=3821 lang=java
 *
 * [3821] Find N-th Smallest Integer With K One Bits
 *
 * Construct the answer from high bit to low bit. With current bit set to 0,
 * there are C(bit, remainingOnes) smaller values. If n exceeds that count, skip
 * them, set this bit to 1, and consume one required one-bit.
 *
 * Java note: binomial coefficients are precomputed in a Pascal table using long.
 *
 * Time: O(50). Space: O(50^2).
 */

// @lc code=start
class Solution {
    public long nthSmallest(long n, int k) {
        long[][] comb = combinations(50);
        long answer = 0;
        int remaining = k;

        for (int bit = 49; bit >= 0; bit--) {
            long countWithZero = remaining >= 0 ? comb[bit][remaining] : 0;
            if (n > countWithZero) {
                n -= countWithZero;
                answer |= 1L << bit;
                remaining--;
                if (remaining == 0) {
                    break;
                }
            }
        }
        return answer;
    }

    private long[][] combinations(int n) {
        long[][] c = new long[n + 1][n + 1];
        for (int i = 0; i <= n; i++) {
            c[i][0] = c[i][i] = 1;
            for (int j = 1; j < i; j++) {
                c[i][j] = c[i - 1][j - 1] + c[i - 1][j];
            }
        }
        return c;
    }
}
// @lc code=end
