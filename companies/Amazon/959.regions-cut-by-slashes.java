/*
 * @lc app=leetcode id=959 lang=java
 *
 * [959] Regions Cut By Slashes
 */

/*
 * --- Interview notes (grid refinement, union–find, slash semantics, complexity) ---
 *
 * Problem
 * An **`n × n`** grid of strings describes each unit square with **`' '`**, **`'/'`**, or **`'\\'`**. Slashes split squares into
 * regions; count **connected** pieces (4-connected through edges **not** blocked by a slash). Return the number of **regions**.
 *
 * Why subdivide each cell
 * A slash only tells us how the **inside** of one square is split. To count connected components globally, we need **nodes** that
 * represent **faces** and **edges** we can glue across cell boundaries. The standard trick is to split each empty square into **four**
 * **triangular** pieces (or quadrants) meeting at the center:
 *
 * ```
 *      0 (top)
 *   3       1   (left)   (right)
 *      2 (bottom)
 * ```
 *
 * Equivalently some solutions label **`0|1 / --- / 2|3`** — same idea: **four sub-regions per cell**, indexed **`0..3`**.
 *
 * Cross-cell adjacency (before handling the character)
 * • **`(i, j)`** **right** triangle **`1`** touches **`(i, j+1)`** **left** triangle **`3`** when **`j+1 < n`**.
 * • **`(i, j)`** **bottom** triangle **`2`** touches **`(i+1, j)`** **top** triangle **`0`** when **`i+1 < n`**.
 *
 * Intra-cell unions (same **`(i, j)`**, base **`b = 4·(i·n + j)`**)
 * • **`' '`** — all four pieces connected: union **`(b+0,b+1)`**, **`(b+1,b+3)`**, **`(b+3,b+2)`**, **`(b+2,b+0)`** (any spanning set).
 * • **`'/'`** — slash rises **bottom-left → top-right** in the character cell; it separates **`{0,3}`** from **`{1,2}`** (pairs across the
 *   diagonal): **`union(b+0,b+3)`**, **`union(b+1,b+2)`**.
 * • **`'\\'`** — separates **`{0,1}`** from **`{2,3}`**: **`union(b+0,b+1)`**, **`union(b+2,b+3)`**.
 *
 * Why union–find (DSU)
 * • **Dynamic connectivity** on **`4·n²`** micro-nodes; **union** merges regions, **find** identifies a component.
 * • Alternatives: **BFS/DFS** on an explicit graph with **`O(n²)`** vertices also works (**`O(n²)`** time), but DSU is compact and easy to
 *   reason about for **merge-only** connectivity.
 *
 * Algorithm
 * 1. **`N = 4 · n²`** DSU nodes.
 * 2. For each cell **`(i, j)`**, union with **left** and **top** neighbors’ matching triangles (boundary glue).
 * 3. Apply **intra-cell** unions from **`grid[i][j]`**.
 * 4. Answer = **number of distinct DSU roots** among **`0 .. N-1`**.
 *
 * Data structures
 * **`parent`** array (**path compression**); optional **`rank`** or **`size`** for union-by-rank — improves asymptotics slightly.
 *
 * Time complexity **`O(n² · α(n²))`** — **`α`** inverse Ackermann, effectively constant; **`O(n²)`** unions/finds.
 *
 * Space complexity **`O(n²)`** for DSU (**`4 n²`** nodes).
 *
 * Edge cases
 * • **`n = 1`**, **`" "`** → **1** region.
 * • **`n = 1`**, **`"/"`** or **`"\\"`** → **2** regions.
 * • Larger grids — slashes + spaces combine across boundaries.
 *
 * Tests (LeetCode)
 * • **`[" /","/ "]`** → **2** regions.
 * • **`[" /","  "]`** → **1** region.
 * • **`["/\\","\\/"]`** → **5** regions.
 *
 * Improvements
 * • **Union by rank / size** keeps trees shallow (already tiny constants here).
 * • **DFS on `3n × 3n`** bitmap is another encoding; same **`O(n²)`** idea with different bookkeeping.
 *
 * --- end notes ---
 */

// @lc code=start
class Solution {
    public int regionsBySlashes(String[] grid) {
        int n = grid.length;
        int n4 = 4 * n * n;
        int[] parent = new int[n4];
        for (int i = 0; i < n4; i++) {
            parent[i] = i;
        }

        for (int i = 0; i < n; i++) {
            for (int j = 0; j < n; j++) {
                if (j > 0) {
                    union(parent, node(i, j, 3, n), node(i, j - 1, 1, n));
                }
                if (i > 0) {
                    union(parent, node(i, j, 0, n), node(i - 1, j, 2, n));
                }

                char c = grid[i].charAt(j);
                int b = node(i, j, 0, n);
                if (c == ' ') {
                    union(parent, b + 0, b + 1);
                    union(parent, b + 1, b + 3);
                    union(parent, b + 3, b + 2);
                    union(parent, b + 2, b + 0);
                } else if (c == '/') {
                    union(parent, b + 0, b + 3);
                    union(parent, b + 1, b + 2);
                } else {
                    union(parent, b + 0, b + 1);
                    union(parent, b + 2, b + 3);
                }
            }
        }

        int count = 0;
        for (int i = 0; i < n4; i++) {
            if (find(parent, i) == i) {
                count++;
            }
        }
        return count;
    }

    private static int node(int i, int j, int k, int n) {
        return (i * n + j) * 4 + k;
    }

    private static int find(int[] parent, int x) {
        while (parent[x] != x) {
            parent[x] = parent[parent[x]];
            x = parent[x];
        }
        return x;
    }

    private static void union(int[] parent, int a, int b) {
        int ra = find(parent, a);
        int rb = find(parent, b);
        if (ra != rb) {
            parent[ra] = rb;
        }
    }
}
// @lc code=end
