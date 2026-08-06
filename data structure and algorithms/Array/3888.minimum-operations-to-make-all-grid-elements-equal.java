/*
 * @lc app=leetcode id=3888 lang=java
 *
 * [3888] Minimum Operations to Make All Grid Elements Equal
 *
 * Greedy row-major with 2D difference array; try target max and max+1.
 */

// @lc code=start
class Solution {
    public int minOperations(int[][] grid, int k) {
        int m = grid.length;
        int n = grid[0].length;
        int mx = Integer.MIN_VALUE;
        for (int[] row : grid) {
            for (int v : row) {
                mx = Math.max(mx, v);
            }
        }

        for (int t = mx; t <= mx + 1; t++) {
            int res = check(grid, m, n, k, t);
            if (res >= 0) {
                return res;
            }
        }
        return -1;
    }

    private int check(int[][] grid, int m, int n, int k, int target) {
        int[][] diff = new int[m + 2][n + 2];
        int total = 0;

        for (int i = 1; i <= m; i++) {
            for (int j = 1; j <= n; j++) {
                diff[i][j] += diff[i - 1][j] + diff[i][j - 1] - diff[i - 1][j - 1];

                int val = grid[i - 1][j - 1];
                int cur = val + diff[i][j];

                if (cur > target) {
                    return -1;
                }
                if (cur < target) {
                    if (i + k - 1 > m || j + k - 1 > n) {
                        return -1;
                    }
                    int need = target - cur;
                    total += need;
                    diff[i][j] += need;
                    diff[i + k][j] -= need;
                    diff[i][j + k] -= need;
                    diff[i + k][j + k] += need;
                }
            }
        }
        return total;
    }
}
// @lc code=end
