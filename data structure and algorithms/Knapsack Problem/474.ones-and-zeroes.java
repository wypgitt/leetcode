/*
 * @lc app=leetcode id=474 lang=java
 *
 * [474] Ones and Zeroes
 *
 * 0/1 knapsack with two capacities: zeros and ones. Iterate capacities
 * backward for each string so every string is used at most once.
 *
 * Time: O(len(strs) * m * n). Space: O(mn).
 */

// @lc code=start
class Solution {
    public int findMaxForm(String[] strs, int m, int n) {
        int[][] dp = new int[m + 1][n + 1];

        for (String text : strs) {
            int zeroes = 0;
            for (int i = 0; i < text.length(); i++) {
                if (text.charAt(i) == '0') {
                    zeroes++;
                }
            }
            int ones = text.length() - zeroes;

            for (int z = m; z >= zeroes; z--) {
                for (int o = n; o >= ones; o--) {
                    dp[z][o] = Math.max(dp[z][o], dp[z - zeroes][o - ones] + 1);
                }
            }
        }
        return dp[m][n];
    }
}
// @lc code=end
