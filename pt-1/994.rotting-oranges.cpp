/*
 * @lc app=leetcode id=994 lang=cpp
 *
 * [994] Rotting Oranges
 */
// Translated from 994.rotting-oranges.py.
// Original Python source and explanation are preserved below as comments.
// #
// # lc-original app=leetcode id=994 lang=python3
// #
// # [994] Rotting Oranges
// #
// 
// # --- Interview notes (multi-source BFS, level = minute, grid states, complexity, edges, alternatives) ---
// #
// # Problem
// # `m × n` grid: `0` empty, `1` fresh orange, `2` rotten. Each minute, every rotten orange **simultaneously** rots **4-neighbor**
// # (up/down/left/right) fresh oranges; rot spreads in parallel like discrete time steps. Return **minimum minutes** until no
// # cell has value `1`, or **-1** if some fresh orange can never be reached.
// #
// # Why BFS (not DFS for shortest time)
// # Each minute advances **one layer** of Manhattan expansion from all rotten sources — unweighted shortest “time” to each
// # cell from **nearest** rotten origin. **Multi-source BFS** from all initial `2` cells explores frontier wavefronts in lockstep
// # with global minimum elapsed minutes — exactly the physical process.
// #
// # Algorithm
// # 1. Scan grid: count **fresh** oranges; enqueue all **rotten** coordinates in a queue.
// # 2. If `fresh == 0`, return **0** (nothing to wait for).
// # 3. **Level-order BFS**: while queue non-empty, process **current frontier** (`len(q)` cells), rotting adjacent fresh cells
// #    (mark `2`, decrement `fresh`, enqueue new positions). After finishing one frontier, if the queue still has cells,
// #    increment **minutes** (another minute will elapse before those cells spread further).
// # 4. End: if `fresh == 0`, return accumulated minutes; else **-1** (unreachable fresh remains).
// #
// # Minute accounting (why `if q: ans += 1` after each layer)
// # After processing all oranges that are rotten at the **start** of a minute, anything newly added to the queue will rot
// # **their** neighbors in the **next** minute. Increment only when there is a **next** frontier left to process — avoids
// # counting an extra minute after the last infections have finished (validated by tracing 1–cell chains).
// #
// # Data structures
// # • **`collections.deque`** — O(1) pop-left / append for FIFO BFS.
// # • **In-place grid mutation** `1 → 2` — acts as **visited** set (no separate `seen` matrix).
// #
// # Time complexity **O(m·n)** — each cell enqueued/dequeued at most once.
// #
// # Space complexity **O(m·n)** — worst-case queue size (e.g. many rotten cells).
// #
// # Edge cases
// # • All fresh unreachable (no rotten, or disconnected regions) → **-1** after BFS if `fresh > 0`.
// # • Already no fresh → **0**.
// # • Single rotten infecting all → minutes = max BFS depth from multi-source view.
// #
// # Tests (LeetCode statement)
// # • `[[2,1,1],[1,1,0],[0,1,1]]` → **4** (last row middle/right stay reachable along fresh cells).
// # • `[[2,1,1],[0,1,1],[1,0,1]]` → **-1** (a fresh orange never touches rot).
// # • `[[0,2]]` → **0** (no fresh oranges).
// #
// # Improvements / variants
// # • Store `(r, c, t)` in queue and track **max t** instead of layer counting — same asymptotics, slightly more memory.
// # • Do not mutate input if forbidden — copy grid or use `visited` set (**O(m·n)** extra space).
// #
// # --- end notes ---
// 
// # lc-original code=start
// from collections import deque
// from typing import List
// 
// 
// class Solution:
//     def orangesRotting(self, grid: List[List[int]]) -> int:
//         m, n = len(grid), len(grid[0])
//         q = deque()
//         fresh = 0
//         for i in range(m):
//             for j in range(n):
//                 if grid[i][j] == 1:
//                     fresh += 1
//                 elif grid[i][j] == 2:
//                     q.append((i, j))
// 
//         if fresh == 0:
//             return 0
// 
//         ans = 0
//         dirs = (0, 1), (0, -1), (1, 0), (-1, 0)
//         while q:
//             for _ in range(len(q)):
//                 i, j = q.popleft()
//                 for di, dj in dirs:
//                     ni, nj = i + di, j + dj
//                     if 0 <= ni < m and 0 <= nj < n and grid[ni][nj] == 1:
//                         grid[ni][nj] = 2
//                         fresh -= 1
//                         q.append((ni, nj))
//             if q:
//                 ans += 1
// 
//         return ans if fresh == 0 else -1
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
    int orangesRotting(vector<vector<int>>& grid) {
        int m = grid.size(), n = grid[0].size();
        queue<pair<int, int>> q;
        int fresh = 0;
        for (int i = 0; i < m; ++i) for (int j = 0; j < n; ++j) {
            if (grid[i][j] == 1) ++fresh;
            else if (grid[i][j] == 2) q.push({i, j});
        }
        if (fresh == 0) return 0;
        int ans = 0, dirs[5] = {0, 1, 0, -1, 0};
        while (!q.empty()) {
            int sz = q.size();
            while (sz--) {
                auto [i, j] = q.front();
                q.pop();
                for (int d = 0; d < 4; ++d) {
                    int ni = i + dirs[d], nj = j + dirs[d + 1];
                    if (0 <= ni && ni < m && 0 <= nj && nj < n && grid[ni][nj] == 1) {
                        grid[ni][nj] = 2;
                        --fresh;
                        q.push({ni, nj});
                    }
                }
            }
            if (!q.empty()) ++ans;
        }
        return fresh == 0 ? ans : -1;
    }
};
// @lc code=end
