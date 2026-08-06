/*
 * @lc app=leetcode id=3882 lang=java
 *
 * [3882] Minimum XOR Path in a Grid
 *
 * Standard grid DP, but each cell can have many reachable XOR values. dp[col]
 * stores the set of XORs reaching the current row's cell in that column; combine
 * from top and left, xor with the current value, and keep the final minimum.
 *
 * Time: O(rows * cols * states). Space: O(cols * states).
 */

import java.util.HashSet;
import java.util.Set;

// @lc code=start
class Solution {
    public int minCost(int[][] grid) {
        int rows = grid.length;
        int cols = grid[0].length;
        Set<Integer>[] dp = new HashSet[cols];
        for (int c = 0; c < cols; c++) {
            dp[c] = new HashSet<>();
        }

        for (int r = 0; r < rows; r++) {
            for (int c = 0; c < cols; c++) {
                int value = grid[r][c];
                if (r == 0 && c == 0) {
                    dp[c] = new HashSet<>();
                    dp[c].add(value);
                    continue;
                }

                Set<Integer> reachable = new HashSet<>();
                if (r > 0) {
                    for (int previous : dp[c]) {
                        reachable.add(previous ^ value);
                    }
                }
                if (c > 0) {
                    for (int previous : dp[c - 1]) {
                        reachable.add(previous ^ value);
                    }
                }
                dp[c] = reachable;
            }
        }

        int answer = Integer.MAX_VALUE;
        for (int value : dp[cols - 1]) {
            answer = Math.min(answer, value);
        }
        return answer;
    }
}
// @lc code=end
