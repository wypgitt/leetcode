class Solution {
    public int countServers(int[][] grid) {
        int rows = grid.length;
        int cols = grid[0].length;
        int[] rowCount = new int[rows];
        int[] colCount = new int[cols];

        for (int r = 0; r < rows; r++) {
            for (int c = 0; c < cols; c++) {
                if (grid[r][c] == 1) {
                    rowCount[r]++;
                    colCount[c]++;
                }
            }
        }

        int total = 0;
        for (int r = 0; r < rows; r++) {
            for (int c = 0; c < cols; c++) {
                if (grid[r][c] == 1 && (rowCount[r] > 1 || colCount[c] > 1)) {
                    total++;
                }
            }
        }

        return total;
    }
}

/*
Explanation

A server communicates if another server exists in its row or column. Precompute
row counts and column counts, then classify every server in O(1).

Two int arrays are the right data structures because they avoid rescanning a
row and column for each server.

Edge cases: isolated server is not counted; two servers sharing a row both
count; all-zero grid returns 0.

Time complexity: O(mn).
Space complexity: O(m + n).
*/
