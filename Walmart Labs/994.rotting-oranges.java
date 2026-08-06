/*
 * @lc app=leetcode id=994 lang=java
 *
 * [994] Rotting Oranges
 */

/*
 * --- Interview notes (multi-source BFS, level = minute, grid states, complexity, edges, alternatives) ---
 *
 * Problem
 * `m × n` grid: `0` empty, `1` fresh orange, `2` rotten. Each minute, every rotten orange **simultaneously** rots **4-neighbor**
 * (up/down/left/right) fresh oranges; rot spreads in parallel like discrete time steps. Return **minimum minutes** until no
 * cell has value `1`, or **-1** if some fresh orange can never be reached.
 *
 * Why BFS (not DFS for shortest time)
 * Each minute advances **one layer** of Manhattan expansion from all rotten sources — unweighted shortest “time” to each
 * cell from **nearest** rotten origin. **Multi-source BFS** from all initial `2` cells explores frontier wavefronts in lockstep
 * with global minimum elapsed minutes — exactly the physical process.
 *
 * Algorithm
 * 1. Scan grid: count **fresh** oranges; enqueue all **rotten** coordinates in a queue.
 * 2. If `fresh == 0`, return **0** (nothing to wait for).
 * 3. **Level-order BFS**: while queue non-empty, process **current frontier** (`len(q)` cells), rotting adjacent fresh cells
 *    (mark `2`, decrement `fresh`, enqueue new positions). After finishing one frontier, if the queue still has cells,
 *    increment **minutes** (another minute will elapse before those cells spread further).
 * 4. End: if `fresh == 0`, return accumulated minutes; else **-1** (unreachable fresh remains).
 *
 * Minute accounting (why `if q: ans += 1` after each layer)
 * After processing all oranges that are rotten at the **start** of a minute, anything newly added to the queue will rot
 * **their** neighbors in the **next** minute. Increment only when there is a **next** frontier left to process — avoids
 * counting an extra minute after the last infections have finished (validated by tracing 1–cell chains).
 *
 * Data structures
 * • **`Deque`** — O(1) poll / offer for FIFO BFS.
 * • **In-place grid mutation** `1 → 2` — acts as **visited** set (no separate `seen` matrix).
 *
 * Time complexity **O(m·n)** — each cell enqueued/dequeued at most once.
 *
 * Space complexity **O(m·n)** — worst-case queue size (e.g. many rotten cells).
 *
 * Edge cases
 * • All fresh unreachable (no rotten, or disconnected regions) → **-1** after BFS if `fresh > 0`.
 * • Already no fresh → **0**.
 * • Single rotten infecting all → minutes = max BFS depth from multi-source view.
 *
 * Tests (LeetCode statement)
 * • `[[2,1,1],[1,1,0],[0,1,1]]` → **4** (last row middle/right stay reachable along fresh cells).
 * • `[[2,1,1],[0,1,1],[1,0,1]]` → **-1** (a fresh orange never touches rot).
 * • `[[0,2]]` → **0** (no fresh oranges).
 *
 * Improvements / variants
 * • Store `(r, c, t)` in queue and track **max t** instead of layer counting — same asymptotics, slightly more memory.
 * • Do not mutate input if forbidden — copy grid or use `visited` set (**O(m·n)** extra space).
 *
 * --- end notes ---
 */

// @lc code=start
import java.util.ArrayDeque;
import java.util.Deque;

class Solution {
    public int orangesRotting(int[][] grid) {
        int m = grid.length;
        int n = grid[0].length;
        Deque<int[]> q = new ArrayDeque<>();
        int fresh = 0;
        for (int i = 0; i < m; i++) {
            for (int j = 0; j < n; j++) {
                if (grid[i][j] == 1) {
                    fresh++;
                } else if (grid[i][j] == 2) {
                    q.offer(new int[] {i, j});
                }
            }
        }

        if (fresh == 0) {
            return 0;
        }

        int ans = 0;
        int[][] dirs = {{0, 1}, {0, -1}, {1, 0}, {-1, 0}};
        while (!q.isEmpty()) {
            int sz = q.size();
            for (int t = 0; t < sz; t++) {
                int[] cell = q.poll();
                int i = cell[0];
                int j = cell[1];
                for (int[] d : dirs) {
                    int ni = i + d[0];
                    int nj = j + d[1];
                    if (ni >= 0 && ni < m && nj >= 0 && nj < n && grid[ni][nj] == 1) {
                        grid[ni][nj] = 2;
                        fresh--;
                        q.offer(new int[] {ni, nj});
                    }
                }
            }
            if (!q.isEmpty()) {
                ans++;
            }
        }

        return fresh == 0 ? ans : -1;
    }
}
// @lc code=end
