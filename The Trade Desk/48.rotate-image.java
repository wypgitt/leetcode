/**
 * Algorithm:
 * Rotate 90 degrees clockwise by transposing the matrix and reversing each row.
 * This performs the rotation in place.
 *
 * Complexity:
 * Time O(n^2), space O(1).
 */
class Solution {
    public void rotate(int[][] matrix) {
        int n = matrix.length;
        for (int r = 0; r < n; r++) {
            for (int c = r + 1; c < n; c++) {
                int tmp = matrix[r][c];
                matrix[r][c] = matrix[c][r];
                matrix[c][r] = tmp;
            }
        }
        for (int[] row : matrix) {
            reverse(row);
        }
    }

    private void reverse(int[] row) {
        int left = 0;
        int right = row.length - 1;
        while (left < right) {
            int tmp = row[left];
            row[left++] = row[right];
            row[right--] = tmp;
        }
    }
}

