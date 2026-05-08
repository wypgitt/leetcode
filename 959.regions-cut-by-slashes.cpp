// Translated from 959.regions-cut-by-slashes.py.
// Original Python source and explanation are preserved below as comments.
// #
// # @lc app=leetcode id=959 lang=python3
// #
// # [959] Regions Cut By Slashes
// #
// 
// # --- Interview notes (grid refinement, union–find, slash semantics, complexity) ---
// #
// # Problem
// # An **`n × n`** grid of strings describes each unit square with **`' '`**, **`'/'`**, or **`'\\'`**. Slashes split squares into
// # regions; count **connected** pieces (4-connected through edges **not** blocked by a slash). Return the number of **regions**.
// #
// # Why subdivide each cell
// # A slash only tells us how the **inside** of one square is split. To count connected components globally, we need **nodes** that
// # represent **faces** and **edges** we can glue across cell boundaries. The standard trick is to split each empty square into **four**
// # **triangular** pieces (or quadrants) meeting at the center:
// #
// # ```
// #      0 (top)
// #   3       1   (left)   (right)
// #      2 (bottom)
// # ```
// #
// # Equivalently some solutions label **`0|1 / --- / 2|3`** — same idea: **four sub-regions per cell**, indexed **`0..3`**.
// #
// # Cross-cell adjacency (before handling the character)
// # • **`(i, j)`** **right** triangle **`1`** touches **`(i, j+1)`** **left** triangle **`3`** when **`j+1 < n`**.
// # • **`(i, j)`** **bottom** triangle **`2`** touches **`(i+1, j)`** **top** triangle **`0`** when **`i+1 < n`**.
// #
// # Intra-cell unions (same **`(i, j)`**, base **`b = 4·(i·n + j)`**)
// # • **`' '`** — all four pieces connected: union **`(b+0,b+1)`**, **`(b+1,b+3)`**, **`(b+3,b+2)`**, **`(b+2,b+0)`** (any spanning set).
// # • **`'/'`** — slash rises **bottom-left → top-right** in the character cell; it separates **`{0,3}`** from **`{1,2}`** (pairs across the
// #   diagonal): **`union(b+0,b+3)`**, **`union(b+1,b+2)`**.
// # • **`'\\'`** — separates **`{0,1}`** from **`{2,3}`**: **`union(b+0,b+1)`**, **`union(b+2,b+3)`**.
// #
// # Why union–find (DSU)
// # • **Dynamic connectivity** on **`4·n²`** micro-nodes; **union** merges regions, **find** identifies a component.
// # • Alternatives: **BFS/DFS** on an explicit graph with **`O(n²)`** vertices also works (**`O(n²)`** time), but DSU is compact and easy to
// #   reason about for **merge-only** connectivity.
// #
// # Algorithm
// # 1. **`N = 4 · n²`** DSU nodes.
// # 2. For each cell **`(i, j)`**, union with **left** and **top** neighbors’ matching triangles (boundary glue).
// # 3. Apply **intra-cell** unions from **`grid[i][j]`**.
// # 4. Answer = **number of distinct DSU roots** among **`0 .. N-1`**.
// #
// # Data structures
// # **`parent`** array (**path compression**); optional **`rank`** or **`size`** for union-by-rank — improves asymptotics slightly.
// #
// # Time complexity **`O(n² · α(n²))`** — **`α`** inverse Ackermann, effectively constant; **`O(n²)`** unions/finds.
// #
// # Space complexity **`O(n²)`** for DSU (**`4 n²`** nodes).
// #
// # Edge cases
// # • **`n = 1`**, **`" "`** → **1** region.
// # • **`n = 1`**, **`"/"`** or **`"\\"`** → **2** regions.
// # • Larger grids — slashes + spaces combine across boundaries.
// #
// # Tests (LeetCode)
// # • **`[" /","/ "]`** → **2** regions.
// # • **`[" /","  "]`** → **1** region.
// # • **`["/\\","\\/"]`** → **5** regions.
// #
// # Improvements
// # • **Union by rank / size** keeps trees shallow (already tiny constants here).
// # • **DFS on `3n × 3n`** bitmap is another encoding; same **`O(n²)`** idea with different bookkeeping.
// #
// # --- end notes ---
// 
// # @lc code=start
// from typing import List
// 
// 
// class Solution:
//     def regionsBySlashes(self, grid: List[str]) -> int:
//         n = len(grid)
//         n4 = 4 * n * n
//         parent = list(range(n4))
// 
//         def find(x: int) -> int:
//             while parent[x] != x:
//                 parent[x] = parent[parent[x]]
//                 x = parent[x]
//             return x
// 
//         def union(a: int, b: int) -> None:
//             ra, rb = find(a), find(b)
//             if ra != rb:
//                 parent[ra] = rb
// 
//         def node(i: int, j: int, k: int) -> int:
//             return (i * n + j) * 4 + k
// 
//         for i in range(n):
//             for j in range(n):
//                 if j > 0:
//                     union(node(i, j, 3), node(i, j - 1, 1))
//                 if i > 0:
//                     union(node(i, j, 0), node(i - 1, j, 2))
// 
//                 c = grid[i][j]
//                 b = node(i, j, 0)
//                 if c == " ":
//                     union(b + 0, b + 1)
//                     union(b + 1, b + 3)
//                     union(b + 3, b + 2)
//                     union(b + 2, b + 0)
//                 elif c == "/":
//                     union(b + 0, b + 3)
//                     union(b + 1, b + 2)
//                 else:
//                     union(b + 0, b + 1)
//                     union(b + 2, b + 3)
// 
//         roots = {find(i) for i in range(n4)}
//         return len(roots)
// 
// 
// # @lc code=end

#include <algorithm>
#include <array>
#include <cctype>
#include <climits>
#include <cmath>
#include <cstdio>
#include <cstdlib>
#include <deque>
#include <fstream>
#include <functional>
#include <iomanip>
#include <iostream>
#include <limits>
#include <map>
#include <numeric>
#include <queue>
#include <random>
#include <set>
#include <sstream>
#include <string>
#include <tuple>
#include <unordered_map>
#include <unordered_set>
#include <utility>
#include <vector>
using namespace std;

// C++ translation notes:
// - Python list/deque/heap/dict/set are translated to vector/deque/priority_queue/map or unordered_map/set.
// - TreeNode and ListNode are supplied by LeetCode. Define LOCAL_LEETCODE_STUBS for local-only compilation of tree/list solutions.
#ifdef LOCAL_LEETCODE_STUBS
struct ListNode {
    int val;
    ListNode* next;
    ListNode() : val(0), next(nullptr) {}
    ListNode(int x) : val(x), next(nullptr) {}
    ListNode(int x, ListNode* next) : val(x), next(next) {}
};
struct TreeNode {
    int val;
    TreeNode* left;
    TreeNode* right;
    TreeNode() : val(0), left(nullptr), right(nullptr) {}
    TreeNode(int x) : val(x), left(nullptr), right(nullptr) {}
    TreeNode(int x, TreeNode* left, TreeNode* right) : val(x), left(left), right(right) {}
};
#endif

class Solution {
public:
    int regionsBySlashes(vector<string>& grid) {
        int n = grid.size(), total = 4 * n * n;
        vector<int> parent(total);
        iota(parent.begin(), parent.end(), 0);
        function<int(int)> find = [&](int x) { return parent[x] == x ? x : parent[x] = find(parent[x]); };
        auto unite = [&](int a, int b) {
            int ra = find(a), rb = find(b);
            if (ra != rb) parent[ra] = rb;
        };
        auto node = [&](int i, int j, int k) { return (i * n + j) * 4 + k; };
        for (int i = 0; i < n; ++i) for (int j = 0; j < n; ++j) {
            if (j > 0) unite(node(i, j, 3), node(i, j - 1, 1));
            if (i > 0) unite(node(i, j, 0), node(i - 1, j, 2));
            int b = node(i, j, 0);
            char c = grid[i][j];
            if (c == ' ') {
                unite(b, b + 1); unite(b + 1, b + 3); unite(b + 3, b + 2); unite(b + 2, b);
            } else if (c == '/') {
                unite(b, b + 3); unite(b + 1, b + 2);
            } else {
                unite(b, b + 1); unite(b + 2, b + 3);
            }
        }
        set<int> roots;
        for (int i = 0; i < total; ++i) roots.insert(find(i));
        return roots.size();
    }
};
