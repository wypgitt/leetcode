/**
 * Algorithm:
 * Simulate row by row. Each glass keeps at most 1 cup; any overflow is split
 * equally to the two glasses below.
 *
 * Java data structures:
 * A double[] stores only the current row, reducing space from the full triangle
 * to O(query_row).
 *
 * Complexity:
 * Time O(query_row^2), space O(query_row).
 */
class Solution {
    public double champagneTower(int poured, int query_row, int query_glass) {
        double[] row = {poured};
        for (int r = 0; r < query_row; r++) {
            double[] next = new double[row.length + 1];
            for (int i = 0; i < row.length; i++) {
                double overflow = Math.max(0.0, row[i] - 1.0) / 2.0;
                next[i] += overflow;
                next[i + 1] += overflow;
            }
            row = next;
        }
        return Math.min(1.0, row[query_glass]);
    }
}

