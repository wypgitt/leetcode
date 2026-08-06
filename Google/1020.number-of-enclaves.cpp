/*
 * @lc app=leetcode id=1020 lang=cpp
 *
 * [1020] Number Of Enclaves
 */
// Translated from 1020.number-of-enclaves.py.
// Original Python source and explanation are preserved below as comments.
// #
// # lc-original app=leetcode id=1020 lang=python3
// #
// # [1020] Number Of Enclaves
// #
// 
// # --- Interview notes (connectivity to boundary, multi-source BFS/DFS, flood fill, complexity, edges) ---
// #
// # Problem
// # Binary grid: **`1`** land, **`0`** water. Move **4-directionally** on land only. An **enclave** is a land cell that **cannot**
// # reach any cell on the **border** of the grid through land cells. Return how many **`1`** cells are enclaves.
// #
// # Equivalent characterization
// # Land cells that lie in the same connected component as **some** border land cell are **not** enclaves (they can “escape” to
// # the frame). All other **`1`** cells are trapped strictly inside — count them.
// #
// # Algorithm — “remove everything touching the boundary”
// # 1. **Multi-source flood fill** starting from every **`1`** on the **first/last row or first/last column**. Mark visited land
// #    by flipping **`1 → 0`** (or a separate **`visited`** matrix if mutation disallowed).
// # 2. Expand with **BFS** or **DFS** to every **`4`**-neighbor land cell.
// # 3. After removal, **sum remaining `1`** values — each surviving **`1`** is disconnected from the border ⇒ enclave cell.
// #
// # Why not count connected components without boundary contact?
// # Equivalent — components disjoint from the boundary union are exactly enclaves; counting cells is the problem’s ask.
// #
// # Data structures
// # • **`collections.deque`** for **BFS** — **O(1)** pops from front (FIFO layer processing).
// # • **In-place grid mutation** — **O(1)** extra versus **`visited[m][n]`**.
// #
// # Time complexity **O(m · n)** — each cell entered **constant** times across border seeds + BFS.
// #
// # Space complexity **O(m · n)** worst-case **queue** size for BFS (thin snake components); **O(m · n)** recursion stack for DFS
// # skew case — **BFS** avoids deep recursion limits in Python.
// #
// # Edge cases
// # • **Single row or column** — every land touches border ⇒ answer **0** after flood fill clears all **`1`** (unless only water).
// # • **No land** — **0**.
// # • **Full grid of land** — border-connected ⇒ interior cleared… actually entire grid connects to border ⇒ **0** enclaves.
// #
// # Tests (sanity)
// # • Border-connected “donut” hole pattern — inner **`1`** cells counted only if truly sealed from border reachability.
// #
// # Improvements
// # • **Union-Find** over land cells — heavier; flood fill is optimal here.
// # • **DFS** recursive one-liner — fine for small grids; prefer iterative **BFS** for robustness on **`500 × 500`**-style limits.
// #
// # --- end notes ---
// 
// # lc-original code=start
// from collections import deque
// from typing import List
// 
// 
// class Solution:
//     def numEnclaves(self, grid: List[List[int]]) -> int:
//         m, n = len(grid), len(grid[0])
//         q = deque()
//         for i in range(m):
//             for j in range(n):
//                 if (i == 0 or i == m - 1 or j == 0 or j == n - 1) and grid[i][j]:
//                     q.append((i, j))
//                     grid[i][j] = 0
// 
//         dirs = (0, 1), (0, -1), (1, 0), (-1, 0)
//         while q:
//             i, j = q.popleft()
//             for di, dj in dirs:
//                 ni, nj = i + di, j + dj
//                 if 0 <= ni < m and 0 <= nj < n and grid[ni][nj]:
//                     grid[ni][nj] = 0
//                     q.append((ni, nj))
// 
//         return sum(sum(row) for row in grid)
// 
// 
// # lc-original code=end

// @lc code=start
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
    int numEnclaves(vector<vector<int>>& grid) {
        int m = grid.size(), n = grid[0].size();
        queue<pair<int, int>> q;
        for (int i = 0; i < m; ++i) {
            for (int j = 0; j < n; ++j) {
                if ((i == 0 || i == m - 1 || j == 0 || j == n - 1) && grid[i][j]) {
                    grid[i][j] = 0;
                    q.push({i, j});
                }
            }
        }
        int dirs[5] = {0, 1, 0, -1, 0};
        while (!q.empty()) {
            auto [i, j] = q.front();
            q.pop();
            for (int d = 0; d < 4; ++d) {
                int ni = i + dirs[d], nj = j + dirs[d + 1];
                if (0 <= ni && ni < m && 0 <= nj && nj < n && grid[ni][nj]) {
                    grid[ni][nj] = 0;
                    q.push({ni, nj});
                }
            }
        }
        int ans = 0;
        for (auto& row : grid) ans += accumulate(row.begin(), row.end(), 0);
        return ans;
    }
};
// @lc code=end
