/*
 * @lc app=leetcode id=1020 lang=java
 *
 * [1020] Number Of Enclaves
 */

/*
 * --- Interview notes (connectivity to boundary, multi-source BFS/DFS, flood fill, complexity, edges) ---
 *
 * Problem
 * Binary grid: **`1`** land, **`0`** water. Move **4-directionally** on land only. An **enclave** is a land cell that **cannot**
 * reach any cell on the **border** of the grid through land cells. Return how many **`1`** cells are enclaves.
 *
 * Equivalent characterization
 * Land cells that lie in the same connected component as **some** border land cell are **not** enclaves (they can “escape” to
 * the frame). All other **`1`** cells are trapped strictly inside — count them.
 *
 * Algorithm — “remove everything touching the boundary”
 * 1. **Multi-source flood fill** starting from every **`1`** on the **first/last row or first/last column**. Mark visited land
 *    by flipping **`1 → 0`** (or a separate **`visited`** matrix if mutation disallowed).
 * 2. Expand with **BFS** or **DFS** to every **`4`**-neighbor land cell.
 * 3. After removal, **sum remaining `1`** values — each surviving **`1`** is disconnected from the border ⇒ enclave cell.
 *
 * Why not count connected components without boundary contact?
 * Equivalent — components disjoint from the boundary union are exactly enclaves; counting cells is the problem’s ask.
 *
 * Data structures
 * • **`ArrayDeque`** for **BFS** — **O(1)** pops from front (FIFO layer processing).
 * • **In-place grid mutation** — **O(1)** extra versus **`visited[m][n]`**.
 *
 * Time complexity **O(m · n)** — each cell entered **constant** times across border seeds + BFS.
 *
 * Space complexity **O(m · n)** worst-case **queue** size for BFS (thin snake components); **O(m · n)** recursion stack for DFS
 * skew case — **BFS** avoids deep recursion limits.
 *
 * Edge cases
 * • **Single row or column** — every land touches border ⇒ answer **0** after flood fill clears all **`1`** (unless only water).
 * • **No land** — **0**.
 * • **Full grid of land** — border-connected ⇒ entire grid connects to border ⇒ **0** enclaves.
 *
 * Tests (sanity)
 * • Border-connected “donut” hole pattern — inner **`1`** cells counted only if truly sealed from border reachability.
 *
 * Improvements
 * • **Union-Find** over land cells — heavier; flood fill is optimal here.
 * • **DFS** recursive one-liner — fine for small grids; prefer iterative **BFS** for robustness on **`500 × 500`**-style limits.
 *
 * --- end notes ---
 */

import java.util.ArrayDeque;
import java.util.Deque;

// @lc code=start
class Solution {
    public int numEnclaves(int[][] grid) {
        int m = grid.length;
        int n = grid[0].length;
        Deque<int[]> q = new ArrayDeque<>();
        for (int i = 0; i < m; i++) {
            for (int j = 0; j < n; j++) {
                if ((i == 0 || i == m - 1 || j == 0 || j == n - 1) && grid[i][j] == 1) {
                    q.addLast(new int[] {i, j});
                    grid[i][j] = 0;
                }
            }
        }
        int[][] dirs = {{0, 1}, {0, -1}, {1, 0}, {-1, 0}};
        while (!q.isEmpty()) {
            int[] cur = q.pollFirst();
            int i = cur[0];
            int j = cur[1];
            for (int[] d : dirs) {
                int ni = i + d[0];
                int nj = j + d[1];
                if (ni >= 0 && ni < m && nj >= 0 && nj < n && grid[ni][nj] == 1) {
                    grid[ni][nj] = 0;
                    q.addLast(new int[] {ni, nj});
                }
            }
        }
        int sum = 0;
        for (int i = 0; i < m; i++) {
            for (int j = 0; j < n; j++) {
                sum += grid[i][j];
            }
        }
        return sum;
    }
}
// @lc code=end
