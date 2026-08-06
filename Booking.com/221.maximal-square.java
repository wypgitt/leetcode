/**
 * Algorithm:
 * DP where dp[j] is the side length of the largest square ending at the current
 * row and column j. A '1' cell extends by 1 plus min(top, left, top-left).
 *
 * Java data structures:
 * int[] stores one DP row; prevDiag stores the old top-left value.
 *
 * Complexity:
 * Time O(rows * cols), space O(cols).
 */
class Solution {
    public int maximalSquare(char[][] matrix) {
        if (matrix == null || matrix.length == 0 || matrix[0].length == 0) {
            return 0;
        }
        int cols = matrix[0].length;
        int[] dp = new int[cols + 1];
        int best = 0;
        for (char[] row : matrix) {
            int prevDiag = 0;
            for (int j = 1; j <= cols; j++) {
                int top = dp[j];
                if (row[j - 1] == '1') {
                    dp[j] = 1 + Math.min(Math.min(dp[j], dp[j - 1]), prevDiag);
                    best = Math.max(best, dp[j]);
                } else {
                    dp[j] = 0;
                }
                prevDiag = top;
            }
        }
        return best * best;
    }
}

