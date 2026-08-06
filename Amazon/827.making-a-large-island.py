#
# @lc app=leetcode id=827 lang=python3
#
# [827] Making A Large Island
#
# https://leetcode.com/problems/making-a-large-island/description/
#
# algorithms
# Hard (57.03%)
# Likes:    5130
# Dislikes: 101
# Total Accepted:    443K
# Total Submissions: 777K
# Testcase Example:  "[[1,0],[0,1]]"
#
# You are given an n x n binary matrix grid. You are allowed to change at most
# one 0 to be 1.
#
# Return the size of the largest island in grid after applying this operation.
#
# An island is a 4-directionally connected group of 1s.
#
# Example 1:
#
# Input: grid = [[1,0],[0,1]]
# Output: 3
# Explanation: Change one 0 to 1 and connect two 1s, then we get an island with
# area = 3.
#
# Example 2:
#
# Input: grid = [[1,1],[1,0]]
# Output: 4
# Explanation: Change the 0 to 1 and make the island bigger, only one island
# with area = 4.
#
# Example 3:
#
# Input: grid = [[1,1],[1,1]]
# Output: 4
# Explanation: Can't change any 0 to 1, only one island with area = 4.
#
# Constraints:
#
# n == grid.length
#
# n == grid[i].length
#
# 1 <= n <= 500
#
# grid[i][j] is either 0 or 1.
#

# @lc code=start

from typing import List


class Solution:
    def largestIsland(self, grid: List[List[int]]) -> int:
        """
        Interview explanation:
        Paint each island with a unique id and record its size (DFS). For each
        0, sum sizes of distinct neighboring islands (+1). Also consider all-1s.

        Algorithm (DFS paint):
        - id from 2; area[id]=size; for each 0 check unique neighbor ids.

        Complexity: O(n^2) time/space.
        """
        n = len(grid)
        area = {0: 0}
        island_id = 2

        def dfs(i: int, j: int, iid: int) -> int:
            if i < 0 or i >= n or j < 0 or j >= n or grid[i][j] != 1:
                return 0
            grid[i][j] = iid
            return 1 + dfs(i + 1, j, iid) + dfs(i - 1, j, iid) + dfs(i, j + 1, iid) + dfs(i, j - 1, iid)

        for i in range(n):
            for j in range(n):
                if grid[i][j] == 1:
                    area[island_id] = dfs(i, j, island_id)
                    island_id += 1

        ans = max(area.values(), default=0)
        dirs = ((1, 0), (-1, 0), (0, 1), (0, -1))
        for i in range(n):
            for j in range(n):
                if grid[i][j] == 0:
                    seen = set()
                    cur = 1
                    for di, dj in dirs:
                        ni, nj = i + di, j + dj
                        if 0 <= ni < n and 0 <= nj < n:
                            iid = grid[ni][nj]
                            if iid > 1 and iid not in seen:
                                seen.add(iid)
                                cur += area[iid]
                    ans = max(ans, cur)
        return ans

    def largestIsland_uf(self, grid: List[List[int]]) -> int:
        """
        Interview explanation:
        Union-Find alternate: union adjacent 1s, then for each 0 try connecting
        neighboring components — same paint-island idea with UF.

        Algorithm:
        - UF on n*n; union 4-neighbors of 1s; for each 0 sum unique parents.

        Complexity: O(n^2 α(n^2)) time, O(n^2) space.
        """
        n = len(grid)
        N = n * n
        parent = list(range(N))
        size = [1] * N

        def find(x: int) -> int:
            while parent[x] != x:
                parent[x] = parent[parent[x]]
                x = parent[x]
            return x

        def union(a: int, b: int) -> None:
            ra, rb = find(a), find(b)
            if ra == rb:
                return
            if size[ra] < size[rb]:
                ra, rb = rb, ra
            parent[rb] = ra
            size[ra] += size[rb]

        def idx(i: int, j: int) -> int:
            return i * n + j

        for i in range(n):
            for j in range(n):
                if grid[i][j] == 1:
                    for di, dj in ((1, 0), (0, 1)):
                        ni, nj = i + di, j + dj
                        if 0 <= ni < n and 0 <= nj < n and grid[ni][nj] == 1:
                            union(idx(i, j), idx(ni, nj))

        ans = max((size[find(idx(i, j))] for i in range(n) for j in range(n) if grid[i][j] == 1), default=0)
        for i in range(n):
            for j in range(n):
                if grid[i][j] == 0:
                    comps = set()
                    cur = 1
                    for di, dj in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                        ni, nj = i + di, j + dj
                        if 0 <= ni < n and 0 <= nj < n and grid[ni][nj] == 1:
                            r = find(idx(ni, nj))
                            if r not in comps:
                                comps.add(r)
                                cur += size[r]
                    ans = max(ans, cur)
        return ans if ans else 0
# @lc code=end
