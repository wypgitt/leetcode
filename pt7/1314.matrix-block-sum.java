/*
 * LeetCode 1314 - Matrix Block Sum
 */
class Solution {
    public int[][] matrixBlockSum(int[][] mat, int k) {
        int rows = mat.length;
        int cols = mat[0].length;
        int[][] prefix = new int[rows + 1][cols + 1];

        for (int r = 0; r < rows; r++) {
            for (int c = 0; c < cols; c++) {
                prefix[r + 1][c + 1] = mat[r][c]
                        + prefix[r][c + 1]
                        + prefix[r + 1][c]
                        - prefix[r][c];
            }
        }

        int[][] answer = new int[rows][cols];
        for (int r = 0; r < rows; r++) {
            int top = Math.max(0, r - k);
            int bottom = Math.min(rows - 1, r + k);

            for (int c = 0; c < cols; c++) {
                int left = Math.max(0, c - k);
                int right = Math.min(cols - 1, c + k);

                answer[r][c] = prefix[bottom + 1][right + 1]
                        - prefix[top][right + 1]
                        - prefix[bottom + 1][left]
                        + prefix[top][left];
            }
        }

        return answer;
    }
}

/*
 * Interview explanation
 * ---------------------
 * Algorithm:
 * Every output cell asks for the sum of a rectangle. A 2D prefix sum answers
 * any rectangle sum in O(1), so after building the prefix table, each cell is
 * computed by four array reads.
 *
 * Java data structures:
 * `int[][] prefix` has one extra row and column of zeros. This padding makes
 * the rectangle formula uniform even when the rectangle touches the top or left
 * boundary.
 *
 * Edge cases:
 * - k = 0 returns the original cell values.
 * - k larger than the matrix clamps to the whole valid matrix area.
 * - Single-row and single-column matrices still use the same formula.
 *
 * Complexity:
 * Time O(mn), one pass to build prefix and one pass for answers.
 * Space O(mn), for the prefix table and output.
 */
