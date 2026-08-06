import java.util.*;

/**
 * Algorithm:
 * Maintain four boundaries and repeatedly consume top row, right column, bottom
 * row, and left column while shrinking inward. Boundary checks prevent reading
 * the final row or column twice.
 *
 * Complexity:
 * Time O(mn), extra space O(1) excluding output.
 */
class Solution {
    public List<Integer> spiralOrder(int[][] matrix) {
        List<Integer> ans = new ArrayList<>();
        int top = 0;
        int bottom = matrix.length - 1;
        int left = 0;
        int right = matrix[0].length - 1;
        while (top <= bottom && left <= right) {
            for (int c = left; c <= right; c++) {
                ans.add(matrix[top][c]);
            }
            top++;
            for (int r = top; r <= bottom; r++) {
                ans.add(matrix[r][right]);
            }
            right--;
            if (top <= bottom) {
                for (int c = right; c >= left; c--) {
                    ans.add(matrix[bottom][c]);
                }
                bottom--;
            }
            if (left <= right) {
                for (int r = bottom; r >= top; r--) {
                    ans.add(matrix[r][left]);
                }
                left++;
            }
        }
        return ans;
    }
}

