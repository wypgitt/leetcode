import java.util.ArrayDeque;
import java.util.Deque;

/*
 * 1020. Number of Enclaves
 */
class Solution {
    public int numEnclaves(int[][] grid) {
        int rows = grid.length;
        int cols = grid[0].length;

        for (int row = 0; row < rows; row++) {
            eraseBoundaryComponent(grid, row, 0);
            eraseBoundaryComponent(grid, row, cols - 1);
        }

        for (int col = 0; col < cols; col++) {
            eraseBoundaryComponent(grid, 0, col);
            eraseBoundaryComponent(grid, rows - 1, col);
        }

        int answer = 0;
        for (int[] row : grid) {
            for (int cell : row) {
                answer += cell;
            }
        }
        return answer;
    }

    private void eraseBoundaryComponent(int[][] grid, int startRow, int startCol) {
        if (grid[startRow][startCol] == 0) {
            return;
        }

        int rows = grid.length;
        int cols = grid[0].length;
        int[][] directions = {{1, 0}, {-1, 0}, {0, 1}, {0, -1}};
        Deque<int[]> stack = new ArrayDeque<>();
        stack.push(new int[] {startRow, startCol});
        grid[startRow][startCol] = 0;

        while (!stack.isEmpty()) {
            int[] cell = stack.pop();
            for (int[] direction : directions) {
                int nextRow = cell[0] + direction[0];
                int nextCol = cell[1] + direction[1];
                if (
                    nextRow >= 0 && nextRow < rows &&
                    nextCol >= 0 && nextCol < cols &&
                    grid[nextRow][nextCol] == 1
                ) {
                    grid[nextRow][nextCol] = 0;
                    stack.push(new int[] {nextRow, nextCol});
                }
            }
        }
    }
}

/*
Interview Explanation

Core idea:
An enclave is land that cannot reach the boundary. Instead of checking every
land cell independently, start from the boundary and remove every land
component that can escape. Whatever land remains is enclosed.

Java data structures:
- int[][] grid stores the matrix and is modified in place.
- ArrayDeque<int[]> is used as an explicit DFS stack. This avoids recursion,
  which is important because the grid can have up to 250,000 cells and Java's
  call stack may overflow on a huge component.

Algorithm:
1. Run DFS from every land cell on the outer border.
2. During DFS, flip reachable land from 1 to 0.
3. Sum the grid. Only unreachable-from-boundary land remains.

Correctness:
Every erased cell has a path of land cells to the boundary, so it is not an
enclave. Any cell not erased cannot have such a path; if it did, the boundary
DFS for that component would have reached it. Therefore the remaining 1s are
exactly the enclave cells.

Complexity:
Each cell is pushed and popped at most once, so time is O(m * n). The stack can
hold O(m * n) cells in the worst case. The grid itself is reused as the visited
marker.

Edge cases:
- All water returns 0.
- All land is completely erased from the boundary, returning 0.
- A single row or column has no enclaves.
- Interior islands surrounded by water remain and are counted.
*/
