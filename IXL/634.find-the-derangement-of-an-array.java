/**
 * Algorithm:
 * Use the derangement recurrence D(n) = (n - 1) * (D(n - 1) + D(n - 2)).
 * Keep only the last two values.
 *
 * Complexity:
 * Time O(n), space O(1).
 */
class Solution {
    public int findDerangement(int n) {
        final int MOD = 1_000_000_007;
        if (n == 1) {
            return 0;
        }
        long prev2 = 1;
        long prev1 = 0;
        for (int i = 2; i <= n; i++) {
            long cur = (i - 1L) * (prev1 + prev2) % MOD;
            prev2 = prev1;
            prev1 = cur;
        }
        return (int) prev1;
    }
}

