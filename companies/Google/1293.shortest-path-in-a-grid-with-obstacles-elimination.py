#
# @lc app=leetcode id=1293 lang=python3
#
# [1293] Shortest Path in a Grid with Obstacles Elimination
#
# https://leetcode.com/problems/shortest-path-in-a-grid-with-obstacles-elimination/description/
#
# algorithms
# Hard (46.6%)
# Likes:    4912
# Dislikes: 91
# Total Accepted:    287K
# Total Submissions: 615K
# Testcase Example:  "[[0,0,0],[1,1,0],[0,0,0],[0,1,1],[0,0,0]]"
#
# You are given an m x n integer matrix grid where each cell is either 0
# (empty) or 1 (obstacle). You can move up, down, left, or right from and to an
# empty cell in one step.
#
# Return the minimum number of steps to walk from the upper left corner (0, 0)
# to the lower right corner (m - 1, n - 1) given that you can eliminate at most
# k obstacles. If it is not possible to find such walk return -1.
#
# Example 1:
#
# Input: grid = [[0,0,0],[1,1,0],[0,0,0],[0,1,1],[0,0,0]], k = 1
# Output: 6
# Explanation:
# The shortest path without eliminating any obstacle is 10.
# The shortest path with one obstacle elimination at position (3,2) is 6. Such
# path is (0,0) -> (0,1) -> (0,2) -> (1,2) -> (2,2) -> (3,2) -> (4,2).
#
# Example 2:
#
# Input: grid = [[0,1,1],[1,1,1],[1,0,0]], k = 1
# Output: -1
# Explanation: We need to eliminate at least two obstacles to find such a walk.
#
# Constraints:
#
# m == grid.length
#
# n == grid[i].length
#
# 1 <= m, n <= 40
#
# 1 <= k <= m * n
#
# grid[i][j] is either 0 or 1.
#
# grid[0][0] == grid[m - 1][n - 1] == 0
#

# @lc code=start

from typing import List
from collections import deque


class Solution:
    def shortestPath(self, grid: List[List[int]], k: int) -> int:
        """
        Interview explanation:
        Shortest path in grid with at most k obstacle eliminations. BFS state
        (r,c,remain_k). Visit (r,c,rk) once with that remaining eliminations
        (or track min obstacles used).

        Algorithm:
        - Queue (r,c,rk,steps); seen[r][c]=max rk seen (or set of rk).
        - Neighbors: if obstacle need rk>0; goal return steps.
        - Return -1 if exhausted.

        Complexity: O(m*n*k) time/space.
        """
        m, n = len(grid), len(grid[0])
        if m == 1 and n == 1:
            return 0
        q = deque([(0, 0, k, 0)])
        seen = {(0, 0, k)}
        while q:
            r, c, rk, steps = q.popleft()
            for dr, dc in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                nr, nc = r + dr, c + dc
                if 0 <= nr < m and 0 <= nc < n:
                    nrk = rk - grid[nr][nc]
                    if nrk < 0:
                        continue
                    if nr == m - 1 and nc == n - 1:
                        return steps + 1
                    state = (nr, nc, nrk)
                    if state not in seen:
                        seen.add(state)
                        q.append((nr, nc, nrk, steps + 1))
        return -1
# @lc code=end
