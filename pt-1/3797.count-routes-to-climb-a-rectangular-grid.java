/*
 * @lc app=leetcode id=3797 lang=java
 *
 * [3797] Count Routes to Climb a Rectangular Grid
 *
 * Dynamic programming from bottom to top. For each row, range-sum windows count
 * optional horizontal moves within distance d, then moves to the row above
 * within floor(sqrt(d^2 - 1)). Prefix sums make each window O(1).
 *
 * Java note: rows are String values; charAt checks blocked cells without
 * converting the whole grid.
 *
 * Time: O(rows * cols). Space: O(cols).
 */

// @lc code=start
class Solution {
    private static final int MOD = 1_000_000_007;

    public int numberOfRoutes(String[] grid, int d) {
        int rows = grid.length;
        int cols = grid[0].length();
        int horizontalRadius = d;
        int upwardRadius = isqrt((long) d * d - 1);

        int[] enter = new int[cols];
        String bottom = grid[rows - 1];
        for (int c = 0; c < cols; c++) {
            enter[c] = bottom.charAt(c) == '.' ? 1 : 0;
        }

        for (int row = rows - 1; row >= 0; row--) {
            int[] afterHorizontal = rangeSums(enter, horizontalRadius, grid[row]);
            if (row == 0) {
                long total = 0;
                for (int value : afterHorizontal) {
                    total += value;
                }
                return (int) (total % MOD);
            }
            enter = rangeSums(afterHorizontal, upwardRadius, grid[row - 1]);
        }
        return 0;
    }

    private int[] rangeSums(int[] values, int radius, String row) {
        int cols = values.length;
        long[] prefix = new long[cols + 1];
        for (int c = 0; c < cols; c++) {
            prefix[c + 1] = (prefix[c] + values[c]) % MOD;
        }

        int[] result = new int[cols];
        for (int c = 0; c < cols; c++) {
            if (row.charAt(c) == '#') {
                continue;
            }
            int left = Math.max(0, c - radius);
            int right = Math.min(cols - 1, c + radius);
            result[c] = (int) ((prefix[right + 1] - prefix[left] + MOD) % MOD);
        }
        return result;
    }

    private int isqrt(long value) {
        int root = (int) Math.sqrt(value);
        while ((long) (root + 1) * (root + 1) <= value) {
            root++;
        }
        while ((long) root * root > value) {
            root--;
        }
        return root;
    }
}
// @lc code=end
