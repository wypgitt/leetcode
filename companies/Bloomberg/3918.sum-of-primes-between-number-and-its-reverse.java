/*
 * @lc app=leetcode id=3918 lang=java
 *
 * [3918] Sum of Primes Between Number and Its Reverse
 *
 * Reverse n, sieve primes up to max(n, reverse), build prefix sums of prime
 * values, and subtract the range before min(n, reverse).
 *
 * Time: O(R log log R). Space: O(R), R = max(n, reverse(n)).
 */

// @lc code=start
class Solution {
    public long sumOfPrimesInRange(int n) {
        int reversed = Integer.parseInt(new StringBuilder(Integer.toString(n)).reverse().toString());
        int left = Math.min(n, reversed);
        int right = Math.max(n, reversed);
        boolean[] isPrime = sieve(right);
        long[] prefix = new long[right + 1];
        for (int value = 1; value <= right; value++) {
            prefix[value] = prefix[value - 1] + (isPrime[value] ? value : 0);
        }
        return prefix[right] - (left > 0 ? prefix[left - 1] : 0);
    }

    private boolean[] sieve(int limit) {
        boolean[] isPrime = new boolean[limit + 1];
        if (limit < 2) {
            return isPrime;
        }
        for (int i = 2; i <= limit; i++) {
            isPrime[i] = true;
        }
        for (int p = 2; p * p <= limit; p++) {
            if (isPrime[p]) {
                for (int multiple = p * p; multiple <= limit; multiple += p) {
                    isPrime[multiple] = false;
                }
            }
        }
        return isPrime;
    }
}
// @lc code=end
