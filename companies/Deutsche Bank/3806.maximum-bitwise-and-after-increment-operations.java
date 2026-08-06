/*
 * @lc app=leetcode id=3806 lang=java
 *
 * [3806] Maximum Bitwise AND After Increment Operations
 *
 * Greedily test answer bits from high to low. For a candidate mask, compute the
 * minimum increment needed for each number to contain every 1-bit in the mask,
 * then choose the m cheapest numbers.
 *
 * Java note: long arithmetic avoids overflow while testing bit 31 and while
 * adding increments.
 *
 * Time: O(B * n log n) for B = 32. Space: O(n).
 */

import java.util.Arrays;

// @lc code=start
class Solution {
    private static final int MAX_BIT = 31;

    public long maximumAND(int[] nums, long k, int m) {
        long answer = 0;
        for (int bit = MAX_BIT; bit >= 0; bit--) {
            long candidate = answer | (1L << bit);
            if (canMake(nums, k, m, candidate)) {
                answer = candidate;
            }
        }
        return answer;
    }

    private boolean canMake(int[] nums, long budget, int count, long mask) {
        long[] costs = new long[nums.length];
        for (int i = 0; i < nums.length; i++) {
            costs[i] = costToContain(nums[i], mask);
        }
        Arrays.sort(costs);
        long total = 0;
        for (int i = 0; i < count; i++) {
            total += costs[i];
            if (total > budget) {
                return false;
            }
        }
        return true;
    }

    private long costToContain(long value, long mask) {
        long target = value;
        for (int bit = MAX_BIT; bit >= 0; bit--) {
            if (((mask >> bit) & 1L) == 1L && ((target >> bit) & 1L) == 0L) {
                target = ((target >> bit) + 1) << bit;
                target |= mask & ((1L << bit) - 1);
            }
        }
        return target - value;
    }
}
// @lc code=end
