#
# @lc app=leetcode id=1020 lang=python3
#
# [1020] Number Of Enclaves
#

# --- Interview notes (connectivity to boundary, multi-source BFS/DFS, flood fill, complexity, edges) ---
#
# Problem
# Binary grid: **`1`** land, **`0`** water. Move **4-directionally** on land only. An **enclave** is a land cell that **cannot**
# reach any cell on the **border** of the grid through land cells. Return how many **`1`** cells are enclaves.
#
# Equivalent characterization
# Land cells that lie in the same connected component as **some** border land cell are **not** enclaves (they can “escape” to
# the frame). All other **`1`** cells are trapped strictly inside — count them.
#
# Algorithm — “remove everything touching the boundary”
# 1. **Multi-source flood fill** starting from every **`1`** on the **first/last row or first/last column**. Mark visited land
#    by flipping **`1 → 0`** (or a separate **`visited`** matrix if mutation disallowed).
# 2. Expand with **BFS** or **DFS** to every **`4`**-neighbor land cell.
# 3. After removal, **sum remaining `1`** values — each surviving **`1`** is disconnected from the border ⇒ enclave cell.
#
# Why not count connected components without boundary contact?
# Equivalent — components disjoint from the boundary union are exactly enclaves; counting cells is the problem’s ask.
#
# Data structures
# • **`collections.deque`** for **BFS** — **O(1)** pops from front (FIFO layer processing).
# • **In-place grid mutation** — **O(1)** extra versus **`visited[m][n]`**.
#
# Time complexity **O(m · n)** — each cell entered **constant** times across border seeds + BFS.
#
# Space complexity **O(m · n)** worst-case **queue** size for BFS (thin snake components); **O(m · n)** recursion stack for DFS
# skew case — **BFS** avoids deep recursion limits in Python.
#
# Edge cases
# • **Single row or column** — every land touches border ⇒ answer **0** after flood fill clears all **`1`** (unless only water).
# • **No land** — **0**.
# • **Full grid of land** — border-connected ⇒ interior cleared… actually entire grid connects to border ⇒ **0** enclaves.
#
# Tests (sanity)
# • Border-connected “donut” hole pattern — inner **`1`** cells counted only if truly sealed from border reachability.
#
# Improvements
# • **Union-Find** over land cells — heavier; flood fill is optimal here.
# • **DFS** recursive one-liner — fine for small grids; prefer iterative **BFS** for robustness on **`500 × 500`**-style limits.
#
# --- end notes ---

# @lc code=start
from collections import deque
from typing import List


class Solution:
    def numEnclaves(self, grid: List[List[int]]) -> int:
        m, n = len(grid), len(grid[0])
        q = deque()
        for i in range(m):
            for j in range(n):
                if (i == 0 or i == m - 1 or j == 0 or j == n - 1) and grid[i][j]:
                    q.append((i, j))
                    grid[i][j] = 0

        dirs = (0, 1), (0, -1), (1, 0), (-1, 0)
        while q:
            i, j = q.popleft()
            for di, dj in dirs:
                ni, nj = i + di, j + dj
                if 0 <= ni < m and 0 <= nj < n and grid[ni][nj]:
                    grid[ni][nj] = 0
                    q.append((ni, nj))

        return sum(sum(row) for row in grid)


# @lc code=end
