class Solution {
    public int countSquares(int[][] matrix) {
        int rows = matrix.length;
        int cols = matrix[0].length;
        int[] prev = new int[cols + 1];
        int total = 0;

        for (int r = 1; r <= rows; r++) {
            int[] curr = new int[cols + 1];
            for (int c = 1; c <= cols; c++) {
                if (matrix[r - 1][c - 1] == 1) {
                    curr[c] = 1 + Math.min(prev[c], Math.min(curr[c - 1], prev[c - 1]));
                    total += curr[c];
                }
            }
            prev = curr;
        }

        return total;
    }
}

/*
Explanation

dp[r][c] is the largest all-ones square ending at cell (r, c). If the cell is
1, it can extend only as far as the minimum of the top, left, and top-left
states plus one.

Every cell with DP value x contributes x squares ending there, one for each
side length from 1 through x. A rolling row is enough because each state only
uses the previous row and current row's left value.

Edge cases: zero cells contribute nothing; one-row and one-column matrices work
naturally; all-ones matrices count nested squares.

Time complexity: O(mn).
Space complexity: O(n).
*/
