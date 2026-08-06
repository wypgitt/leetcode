/**
 * Algorithm:
 * Add every positive day-to-day price increase. This captures the same profit
 * as buying before each rising segment and selling at its end.
 *
 * Complexity:
 * Time O(n), space O(1).
 */
class Solution {
    public int maxProfit(int[] prices) {
        int profit = 0;
        for (int i = 1; i < prices.length; i++) {
            profit += Math.max(0, prices[i] - prices[i - 1]);
        }
        return profit;
    }
}

