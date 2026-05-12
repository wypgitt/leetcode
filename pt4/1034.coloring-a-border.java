import java.util.ArrayDeque;
import java.util.ArrayList;
import java.util.Deque;
import java.util.List;

/*
 * 1034. Coloring A Border
 */
class Solution {
    public int[][] colorBorder(int[][] grid, int row, int col, int color) {
        int rows = grid.length;
        int cols = grid[0].length;
        int original = grid[row][col];
        boolean[][] visited = new boolean[rows][cols];
        int[][] directions = {{1, 0}, {-1, 0}, {0, 1}, {0, -1}};
        List<int[]> borders = new ArrayList<>();
        Deque<int[]> stack = new ArrayDeque<>();

        stack.push(new int[] {row, col});
        visited[row][col] = true;

        while (!stack.isEmpty()) {
            int[] cell = stack.pop();
            int r = cell[0];
            int c = cell[1];
            boolean isBorder = r == 0 || r == rows - 1 || c == 0 || c == cols - 1;

            for (int[] direction : directions) {
                int nextRow = r + direction[0];
                int nextCol = c + direction[1];

                if (nextRow < 0 || nextRow >= rows || nextCol < 0 || nextCol >= cols) {
                    isBorder = true;
                } else if (grid[nextRow][nextCol] != original) {
                    isBorder = true;
                } else if (!visited[nextRow][nextCol]) {
                    visited[nextRow][nextCol] = true;
                    stack.push(new int[] {nextRow, nextCol});
                }
            }

            if (isBorder) {
                borders.add(cell);
            }
        }

        for (int[] cell : borders) {
            grid[cell[0]][cell[1]] = color;
        }

        return grid;
    }
}

/*
Interview Explanation

Core idea:
First find the connected component containing (row, col). A component cell is
on the border if it is on the grid boundary or touches a cell with a different
color.

Java data structures:
- boolean[][] visited separates traversal state from the grid colors.
- ArrayDeque<int[]> is an iterative DFS stack.
- ArrayList<int[]> stores border cells so recoloring happens after traversal.
  Delaying recoloring avoids confusing the DFS when the new color differs from
  the original.

Algorithm:
1. DFS through cells with the original color.
2. For each cell, inspect all four neighbors.
3. Mark it as a border if a neighbor is out of bounds or has a different
   color.
4. Recolor only the collected border cells.

Correctness:
DFS visits exactly the starting connected component because it only moves to
same-color, 4-directionally adjacent cells. The border condition is exactly the
problem definition. Recoloring the collected cells therefore changes every and
only border cell of the component.

Complexity:
Each cell is visited at most once, so time is O(m * n). visited, stack, and the
border list use O(m * n) space in the worst case.

Edge cases:
- Single-cell grid: that cell is a border.
- Whole grid same color: only the outer ring changes.
- New color equals original: result is unchanged but traversal remains valid.
*/
