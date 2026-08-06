/**
 * Algorithm:
 * Fill the matrix using the same four-boundary spiral walk as traversal:
 * right, down, left, up, then shrink inward.
 *
 * Complexity:
 * Time O(n^2), extra space O(1) excluding output.
 */
class Solution {
    public int[][] generateMatrix(int n) {
        int[][] matrix = new int[n][n];
        int top = 0;
        int bottom = n - 1;
        int left = 0;
        int right = n - 1;
        int value = 1;
        while (top <= bottom && left <= right) {
            for (int c = left; c <= right; c++) {
                matrix[top][c] = value++;
            }
            top++;
            for (int r = top; r <= bottom; r++) {
                matrix[r][right] = value++;
            }
            right--;
            for (int c = right; c >= left; c--) {
                matrix[bottom][c] = value++;
            }
            bottom--;
            for (int r = bottom; r >= top; r--) {
                matrix[r][left] = value++;
            }
            left++;
        }
        return matrix;
    }
}

