/*
 * @lc app=leetcode id=931 lang=java
 *
 * [931] Minimum Falling Path Sum
 */

/*
 * --- Interview notes (grid DP, optimal substructure, rolling array, complexity) ---
 *
 * Problem
 * n × n matrix; falling path from any top cell, move to (i+1,j-1), (i+1,j), or (i+1,j+1). Minimize path sum.
 *
 * dp[i][j] = matrix[i][j] + min(prev neighbors). Answer = min_j dp[n-1][j].
 *
 * Space: two rows O(n). Time O(n²).
 *
 * --- end notes ---
 */

// @lc code=start
class Solution {
    public int minFallingPathSum(int[][] matrix) {
        int n = matrix.length;
        if (n == 0) {
            return 0;
        }
        int m = matrix[0].length;
        int[] prev = new int[m];
        System.arraycopy(matrix[0], 0, prev, 0, m);
        for (int i = 1; i < n; i++) {
            int[] cur = new int[m];
            for (int j = 0; j < m; j++) {
                int v = prev[j];
                if (j > 0) {
                    v = Math.min(v, prev[j - 1]);
                }
                if (j + 1 < m) {
                    v = Math.min(v, prev[j + 1]);
                }
                cur[j] = matrix[i][j] + v;
            }
            prev = cur;
        }
        int ans = prev[0];
        for (int j = 1; j < m; j++) {
            ans = Math.min(ans, prev[j]);
        }
        return ans;
    }
}
// @lc code=end
