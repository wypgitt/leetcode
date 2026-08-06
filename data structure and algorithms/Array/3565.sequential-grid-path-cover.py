#
# @lc app=leetcode id=3565 lang=python3
#
# [3565] Sequential Grid Path Cover
#
# https://leetcode.com/problems/sequential-grid-path-cover/description/
#
# algorithms
# Medium (60.22%)
# Likes:    5
# Dislikes: 1
# Total Accepted:    719
# Total Submissions: 1.2K
# Testcase Example:  "[[0,0,0],[0,1,2]]\n2"
#
#
# You are given a 2D array grid of size m x n, and an integer k. There are
# k cells in grid containing the values from 1 to k exactly once, and the
# rest of the cells have a value 0.
#
# You can start at any cell, and move from a cell to its neighbors (up,
# down, left, or right). You must find a path in grid which:
#
# Visits each cell in grid exactly once.
#
# Visits the cells with values from 1 to k in order.
#
# Return a 2D array result of size (m * n) x 2, where result[i] = [x_i,
# y_i] represents the i^th cell visited in the path. If there are multiple
# such paths, you may return any one.
#
# If no such path exists, return an empty array.
#
# Example 1:
#
# Input: grid = [[0,0,0],[0,1,2]], k = 2
#
# Output: [[0,0],[1,0],[1,1],[1,2],[0,2],[0,1]]
#
# Explanation:
#
# Example 2:
#
# Input: grid = [[1,0,4],[3,0,2]], k = 4
#
# Output: []
#
# Explanation:
#
# There is no possible path that satisfies the conditions.
#
# Constraints:
#
# 1 <= m == grid.length <= 5
#
# 1 <= n == grid[i].length <= 5
#
# 1 <= k <= m * n
#
# 0 <= grid[i][j] <= k
#
# grid contains all integers between 1 and k exactly once.
#

# @lc code=start

from typing import List


class Solution:
    def findPath(self, grid: List[List[int]], k: int) -> List[List[int]]:
        """
        Interview explanation:
        Cover every cell exactly once while visiting values 1..k in order.
        Grid is tiny (≤25 cells), so backtracking DFS from every start works.

        Algorithm:
        - next_needed starts at 1; from a cell, move to 4-neighbors unvisited.
        - Entering a positive cell is allowed only if it equals next_needed;
          then increment. Zeros are free.
        - Return the first full-length path; else [].

        Complexity: O((mn)! / branching) worst-case; fine for mn ≤ 25 with
        pruning. Space O(mn).
        """
        m, n = len(grid), len(grid[0])
        total = m * n
        dirs = ((1, 0), (-1, 0), (0, 1), (0, -1))
        path: List[List[int]] = []
        visited = [[False] * n for _ in range(m)]

        def dfs(r: int, c: int, need: int) -> bool:
            val = grid[r][c]
            if val != 0:
                if val != need:
                    return False
                need += 1
            path.append([r, c])
            visited[r][c] = True
            if len(path) == total:
                return need == k + 1
            for dr, dc in dirs:
                nr, nc = r + dr, c + dc
                if 0 <= nr < m and 0 <= nc < n and not visited[nr][nc]:
                    if dfs(nr, nc, need):
                        return True
            path.pop()
            visited[r][c] = False
            return False

        for i in range(m):
            for j in range(n):
                # start cell must be 0 or 1
                if grid[i][j] not in (0, 1):
                    continue
                if dfs(i, j, 1):
                    return path
        return []
# @lc code=end
