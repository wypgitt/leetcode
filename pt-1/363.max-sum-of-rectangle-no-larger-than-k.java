/*
 * @lc app=leetcode id=363 lang=java
 *
 * [363] Max Sum of Rectangle No Larger Than K
 *
 * Compress the smaller dimension pairwise, reducing each fixed-boundary
 * rectangle search to "maximum subarray sum no larger than k". For the 1D
 * problem, store previous prefix sums in a TreeSet and find the smallest
 * previous prefix >= currentPrefix - k.
 *
 * Java note: TreeSet is a red-black tree; ceiling(x) is O(log n), replacing the
 * Python coordinate-compressed Fenwick order search with Java's ordered set.
 *
 * Time: O(min(R,C)^2 * max(R,C) * log max(R,C)). Space: O(max(R,C)).
 */

import java.util.TreeSet;

// @lc code=start
class Solution {
    public int maxSumSubmatrix(int[][] matrix, int k) {
        int rows = matrix.length;
        int cols = matrix[0].length;
        int answer = Integer.MIN_VALUE;

        if (rows <= cols) {
            for (int top = 0; top < rows; top++) {
                int[] columnSums = new int[cols];
                for (int bottom = top; bottom < rows; bottom++) {
                    for (int col = 0; col < cols; col++) {
                        columnSums[col] += matrix[bottom][col];
                    }
                    answer = Math.max(answer, bestSubarrayNoLargerThan(columnSums, k));
                    if (answer == k) {
                        return k;
                    }
                }
            }
        } else {
            for (int left = 0; left < cols; left++) {
                int[] rowSums = new int[rows];
                for (int right = left; right < cols; right++) {
                    for (int row = 0; row < rows; row++) {
                        rowSums[row] += matrix[row][right];
                    }
                    answer = Math.max(answer, bestSubarrayNoLargerThan(rowSums, k));
                    if (answer == k) {
                        return k;
                    }
                }
            }
        }
        return answer;
    }

    private int bestSubarrayNoLargerThan(int[] values, int k) {
        TreeSet<Integer> prefixes = new TreeSet<>();
        prefixes.add(0);
        int prefix = 0;
        int best = Integer.MIN_VALUE;

        for (int value : values) {
            prefix += value;
            Integer previous = prefixes.ceiling(prefix - k);
            if (previous != null) {
                best = Math.max(best, prefix - previous);
            }
            prefixes.add(prefix);
        }
        return best;
    }
}
// @lc code=end
