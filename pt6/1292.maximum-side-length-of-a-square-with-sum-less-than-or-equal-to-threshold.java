class Solution {
    public int maxSideLength(int[][] mat, int threshold) {
        int rows = mat.length;
        int cols = mat[0].length;
        int[][] prefix = new int[rows + 1][cols + 1];

        for (int r = 0; r < rows; r++) {
            int rowSum = 0;
            for (int c = 0; c < cols; c++) {
                rowSum += mat[r][c];
                prefix[r + 1][c + 1] = prefix[r][c + 1] + rowSum;
            }
        }

        int left = 0;
        int right = Math.min(rows, cols);
        while (left < right) {
            int mid = left + (right - left + 1) / 2;
            if (exists(prefix, rows, cols, mid, threshold)) {
                left = mid;
            } else {
                right = mid - 1;
            }
        }

        return left;
    }

    private boolean exists(int[][] prefix, int rows, int cols, int size, int threshold) {
        for (int r = 0; r + size <= rows; r++) {
            for (int c = 0; c + size <= cols; c++) {
                int sum = prefix[r + size][c + size]
                        - prefix[r][c + size]
                        - prefix[r + size][c]
                        + prefix[r][c];
                if (sum <= threshold) {
                    return true;
                }
            }
        }
        return false;
    }
}

/*
Explanation

Build a 2D prefix-sum matrix so any square sum can be queried in O(1). Then
binary search the side length. If a square of size k fits the threshold, every
smaller size is also possible; if none fits, larger sizes are impossible.

The prefix matrix is the core Java data structure because it avoids repeatedly
summing the same cells.

Edge cases: answer 0 when no single cell fits; rectangular matrices; threshold
large enough for the largest possible square.

Time complexity: O(mn log min(m, n)).
Space complexity: O(mn).
*/
