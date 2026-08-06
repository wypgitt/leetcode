/*
 * @lc app=leetcode id=1036 lang=java
 *
 * [1036] Escape a Large Maze
 */

/*
 * --- Interview notes (problem scale, trap lemma, bidirectional check, complexity, edges, tests) ---
 *
 * Problem
 * Grid [0, 10^6)^2. Up to 200 blocked cells. Move 4-neighbor on free cells. Decide if source can reach target.
 *
 * Why we cannot run BFS on the full grid
 * The board has 10^12 cells — any explicit grid storage or full traversal is impossible.
 *
 * Key lemma (small blocker set)
 * With at most B obstacles, any bounded connected component of free cells surrounded “inside” the maze contains
 * at most about B(B−1)/2 cells (tight bound often cited as floor(B²/2) for this problem’s cutoff). Equivalently:
 * if a flood-fill from a start position ever visits strictly more than K = len(blocked)² / 2 distinct cells while
 * staying inside [0, N)² and avoiding blocked squares, that component cannot be locked in a finite trap — it must
 * reach arbitrarily far (and thus can eventually connect to any other point that is also not trapped in a tiny
 * cage). Conversely, if fill stops before exceeding K without reaching the goal, the start might lie in a small
 * enclosed region.
 *
 * Algorithm (contest / editorial)
 * Let K = len(blocked)² // 2.
 * Define walk(A → B): DFS/BFS from A over free cells; maintain visited set; stop with True if
 *   (1) we step on B, or
 *   (2) |visited| > K   (“escaped” the maximal finite enclosure).
 *   Otherwise finish with False (exhausted reachable component without meeting B and without proving escape).
 * Answer is True iff walk(source → target) AND walk(target → source).
 *
 * Why both directions
 * If an undirected path exists, either direction finds the other endpoint when exploring that component.
 * If source sits in a finite pocket that does not contain target, forward walk fails “honestly.” If both ends lie
 * in huge/outside regions but the obstacle pattern somehow disconnects them in a non-obvious way, symmetry check
 * avoids pathological one-sided caveats — standard solution pattern on LeetCode for this problem.
 *
 * Data structures
 * - set of blocked coordinates for O(1) lookup (≤ 200 entries).
 * - set or hash set of visited cells during one walk — bounded by O(K) before early exit, K ≤ 20_000.
 * - explicit stack (DFS) or deque (BFS); iterative DFS avoids Python recursion depth issues on long paths.
 *
 * Time complexity
 * Each walk touches O(min(K, reachable)) cells before stopping → O(K) per walk, two walks → O(K) with tiny constants.
 * Memory O(K) for visited during one walk.
 *
 * Edge cases
 * - blocked empty: K = 0; after placing source in visited, |visited| > 0 is True immediately → both walks True →
 *   connectivity holds for opposite corners (same outside component).
 * - tight enclosure like Example 1: visits stay ≤ K and never reach target → False.
 *
 * Tests (statement)
 * blocked [[0,1],[1,0]], source [0,0], target [0,2] → False.
 * blocked [], source [0,0], target [999999,999999] → True.
 *
 * Improvements
 * - Pack (x, y) into one int key x << 20 | y (both < 2^20) to shave tuple overhead — optional micro-optimization.
 *
 * --- end notes ---
 */

// @lc code=start
import java.util.ArrayDeque;
import java.util.Deque;
import java.util.HashSet;
import java.util.Set;

public class Solution {

    private static final int N = 1_000_000;

    private static long pack(int x, int y) {
        return ((long) x << 20) | y;
    }

    private boolean walk(
            int sx,
            int sy,
            int tx,
            int ty,
            Set<Long> blockedSet,
            int lim) {
        Deque<int[]> stack = new ArrayDeque<>();
        stack.push(new int[] {sx, sy});
        Set<Long> vis = new HashSet<>();
        int[] dirs = {-1, 0, 1, 0, -1};
        while (!stack.isEmpty()) {
            int[] cur = stack.pop();
            int cx = cur[0];
            int cy = cur[1];
            long key = pack(cx, cy);
            if (vis.contains(key)) {
                continue;
            }
            vis.add(key);
            if (vis.size() > lim) {
                return true;
            }
            if (cx == tx && cy == ty) {
                return true;
            }
            for (int k = 0; k < 4; k++) {
                int nx = cx + dirs[k];
                int ny = cy + dirs[k + 1];
                if (nx >= 0 && nx < N && ny >= 0 && ny < N) {
                    if (blockedSet.contains(pack(nx, ny))) {
                        continue;
                    }
                    if (!vis.contains(pack(nx, ny))) {
                        stack.push(new int[] {nx, ny});
                    }
                }
            }
        }
        return false;
    }

    public boolean isEscapePossible(int[][] blocked, int[] source, int[] target) {
        int lim = blocked.length * blocked.length / 2;
        Set<Long> blockedSet = new HashSet<>();
        for (int[] b : blocked) {
            blockedSet.add(pack(b[0], b[1]));
        }
        int sx = source[0];
        int sy = source[1];
        int tx = target[0];
        int ty = target[1];
        return walk(sx, sy, tx, ty, blockedSet, lim) && walk(tx, ty, sx, sy, blockedSet, lim);
    }
}
// @lc code=end
