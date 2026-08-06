/*
 * @lc app=leetcode id=3891 lang=java
 *
 * [3891] Minimum Increase to Maximize Special Indices
 *
 * A peak at i costs max(0, max(nums[i-1], nums[i+1]) + 1 - nums[i]). Adjacent
 * peaks cannot both be selected, so this is house-robber DP where each state
 * stores (number of peaks, total cost) and comparisons maximize count then
 * minimize cost.
 *
 * Time: O(n). Space: O(1).
 */

// @lc code=start
class Solution {
    public long minIncrease(int[] nums) {
        Pair take = new Pair(Long.MIN_VALUE / 4, 0);
        Pair skip = new Pair(0, 0);

        for (int i = 1; i < nums.length - 1; i++) {
            long peakCost = Math.max(0L, Math.max(nums[i - 1], nums[i + 1]) + 1L - nums[i]);
            Pair newTake = new Pair(skip.count + 1, skip.cost + peakCost);
            Pair newSkip = better(take, skip);
            take = newTake;
            skip = newSkip;
        }
        return better(take, skip).cost;
    }

    private Pair better(Pair first, Pair second) {
        if (first.count != second.count) {
            return first.count > second.count ? first : second;
        }
        return first.cost <= second.cost ? first : second;
    }

    private static class Pair {
        final long count;
        final long cost;

        Pair(long count, long cost) {
            this.count = count;
            this.cost = cost;
        }
    }
}
// @lc code=end
