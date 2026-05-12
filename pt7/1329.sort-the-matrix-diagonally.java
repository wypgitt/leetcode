import java.util.HashMap;
import java.util.Map;
import java.util.PriorityQueue;

/*
 * LeetCode 1329 - Sort the Matrix Diagonally
 */
class Solution {
    public int[][] diagonalSort(int[][] mat) {
        int rows = mat.length;
        int cols = mat[0].length;
        Map<Integer, PriorityQueue<Integer>> diagonals = new HashMap<>();

        for (int r = 0; r < rows; r++) {
            for (int c = 0; c < cols; c++) {
                int key = r - c;
                diagonals.computeIfAbsent(key, ignored -> new PriorityQueue<>()).offer(mat[r][c]);
            }
        }

        for (int r = 0; r < rows; r++) {
            for (int c = 0; c < cols; c++) {
                mat[r][c] = diagonals.get(r - c).poll();
            }
        }

        return mat;
    }
}

/*
 * Interview explanation
 * ---------------------
 * Algorithm:
 * Cells on the same top-left to bottom-right diagonal share the same `r - c`.
 * Group values by that key, sort each group, then write the smallest remaining
 * value back while scanning the matrix again.
 *
 * Java data structures:
 * `HashMap<Integer, PriorityQueue<Integer>>` maps each diagonal to a min-heap.
 * The heap gives the next smallest value for that diagonal with `poll()`.
 *
 * Edge cases:
 * - One row or one column: every diagonal has one value.
 * - Duplicate values are naturally supported by the heap.
 * - Rectangular matrices still use the same `r - c` key.
 *
 * Complexity:
 * Time O(mn log d), where d is the maximum diagonal length.
 * Space O(mn), for the grouped heap values.
 */
