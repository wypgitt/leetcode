import java.util.*;

class Solution {
    public int largest1BorderedSquare(int[][] grid) {
        int rows = grid.length;
        int cols = grid[0].length;
        int[][] horizontal = new int[rows][cols];
        int[][] vertical = new int[rows][cols];
        int bestSide = 0;

        for (int r = 0; r < rows; r++) {
            for (int c = 0; c < cols; c++) {
                if (grid[r][c] == 0) {
                    continue;
                }

                horizontal[r][c] = (c == 0 ? 0 : horizontal[r][c - 1]) + 1;
                vertical[r][c] = (r == 0 ? 0 : vertical[r - 1][c]) + 1;
                int side = Math.min(horizontal[r][c], vertical[r][c]);

                while (side > bestSide) {
                    if (vertical[r][c - side + 1] >= side && horizontal[r - side + 1][c] >= side) {
                        bestSide = side;
                        break;
                    }
                    side--;
                }
            }
        }

        return bestSide * bestSide;
    }
}

