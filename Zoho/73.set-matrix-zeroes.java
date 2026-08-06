/**
 * Algorithm:
 * Use the first row and first column as marker arrays for rows/columns that
 * must become zero. Separate booleans remember whether the first row and first
 * column themselves should be zeroed.
 *
 * Complexity:
 * Time O(mn), extra space O(1).
 */
class Solution {
    public void setZeroes(int[][] matrix) {
        int m = matrix.length;
        int n = matrix[0].length;
        boolean firstColZero = false;
        boolean firstRowZero = false;
        for (int r = 0; r < m; r++) {
            if (matrix[r][0] == 0) {
                firstColZero = true;
            }
        }
        for (int c = 0; c < n; c++) {
            if (matrix[0][c] == 0) {
                firstRowZero = true;
            }
        }
        for (int r = 1; r < m; r++) {
            for (int c = 1; c < n; c++) {
                if (matrix[r][c] == 0) {
                    matrix[r][0] = 0;
                    matrix[0][c] = 0;
                }
            }
        }
        for (int r = 1; r < m; r++) {
            for (int c = 1; c < n; c++) {
                if (matrix[r][0] == 0 || matrix[0][c] == 0) {
                    matrix[r][c] = 0;
                }
            }
        }
        if (firstRowZero) {
            for (int c = 0; c < n; c++) {
                matrix[0][c] = 0;
            }
        }
        if (firstColZero) {
            for (int r = 0; r < m; r++) {
                matrix[r][0] = 0;
            }
        }
    }
}

