/*
 * @lc app=leetcode id=3896 lang=java
 *
 * [3896] Minimum Operations to Transform Array Into Alternating Prime
 *
 * Sieve primes up to a safe limit. Even indices are increased to the next prime.
 * Odd indices that are already prime must move away from being prime: 2 needs
 * two operations, any other prime needs one.
 *
 * Java note: nextPrime[value] is filled by scanning the sieve from right to left.
 *
 * Time: O(L log log L + n), L = O(max(nums)). Space: O(L).
 */

// @lc code=start
class Solution {
    public int minOperations(int[] nums) {
        int maxValue = 0;
        for (int value : nums) {
            maxValue = Math.max(maxValue, value);
        }
        int limit = Math.max(10, 2 * maxValue + 10);

        boolean[] isPrime = new boolean[limit + 1];
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

        int[] nextPrime = new int[limit + 1];
        int closest = -1;
        for (int value = limit; value >= 0; value--) {
            if (isPrime[value]) {
                closest = value;
            }
            nextPrime[value] = closest;
        }

        int operations = 0;
        for (int i = 0; i < nums.length; i++) {
            int value = nums[i];
            if ((i & 1) == 0) {
                operations += nextPrime[value] - value;
            } else if (isPrime[value]) {
                operations += value == 2 ? 2 : 1;
            }
        }
        return operations;
    }
}
// @lc code=end
