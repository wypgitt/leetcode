#
# @lc app=leetcode id=2577 lang=python3
#
# [2577] Minimum Time to Visit a Cell In a Grid
#
# https://leetcode.com/problems/minimum-time-to-visit-a-cell-in-a-grid/description/
#
# algorithms
# Hard (56.12%)
# Likes:    1154
# Dislikes: 45
# Total Accepted:    90.6K
# Total Submissions: 161.5K
# Testcase Example:  "[[0,1,3,2],[5,1,2,5],[4,3,8,6]]"
#
# You are given a m x n matrix grid consisting of non-negative integers where
# grid[row][col] represents the minimum time required to be able to visit the
# cell (row, col), which means you can visit the cell (row, col) only when the
# time you visit it is greater than or equal to grid[row][col].
#
# You are standing in the top-left cell of the matrix in the 0^th second, and
# you must move to any adjacent cell in the four directions: up, down, left, and
# right. Each move you make takes 1 second.
#
# Return the minimum time required in which you can visit the bottom-right cell
# of the matrix. If you cannot visit the bottom-right cell, then return -1.
#
#
#
# Example 1:
#
# Input: grid = [[0,1,3,2],[5,1,2,5],[4,3,8,6]]
# Output: 7
# Explanation: One of the paths that we can take is the following:
# - at t = 0, we are on the cell (0,0).
# - at t = 1, we move to the cell (0,1). It is possible because grid[0][1] <= 1.
# - at t = 2, we move to the cell (1,1). It is possible because grid[1][1] <= 2.
# - at t = 3, we move to the cell (1,2). It is possible because grid[1][2] <= 3.
# - at t = 4, we move to the cell (1,1). It is possible because grid[1][1] <= 4.
# - at t = 5, we move to the cell (1,2). It is possible because grid[1][2] <= 5.
# - at t = 6, we move to the cell (1,3). It is possible because grid[1][3] <= 6.
# - at t = 7, we move to the cell (2,3). It is possible because grid[2][3] <= 7.
# The final time is 7. It can be shown that it is the minimum time possible.
#
# Example 2:
#
# Input: grid = [[0,2,4],[3,2,1],[1,0,4]]
# Output: -1
# Explanation: There is no path from the top left to the bottom-right cell.
#
#
#
# Constraints:
#
#
# m == grid.length
#
#
# n == grid[i].length
#
#
# 2 <= m, n <= 1000
#
#
# 4 <= m * n <= 10^5
#
#
# 0 <= grid[i][j] <= 10^5
#
#
# grid[0][0] == 0
#

# @lc code=start
from typing import List
import heapq


class Solution:
    def minimumTime(self, grid: List[List[int]]) -> int:
        """
        Interview explanation:
        Move 4-directionally; enter (i,j) only at time >= grid[i][j]. Each move costs 1.
        You may wait by oscillating on a previous edge (parity +2).

        Algorithm:
        - If both first moves are blocked (grid>1), return -1.
        - Dijkstra for earliest arrival; if t+1 < required, bump to required with correct parity.

        Complexity: O(mn log(mn)) time, O(mn) space.
        """
        m, n = len(grid), len(grid[0])
        if grid[0][1] > 1 and grid[1][0] > 1:
            return -1
        dist = [[10**18] * n for _ in range(m)]
        dist[0][0] = 0
        pq = [(0, 0, 0)]
        while pq:
            t, i, j = heapq.heappop(pq)
            if t != dist[i][j]:
                continue
            if i == m - 1 and j == n - 1:
                return t
            for di, dj in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                ni, nj = i + di, j + dj
                if 0 <= ni < m and 0 <= nj < n:
                    nt = t + 1
                    if nt < grid[ni][nj]:
                        if (grid[ni][nj] - t) % 2 == 0:
                            nt = grid[ni][nj] + 1
                        else:
                            nt = grid[ni][nj]
                    if nt < dist[ni][nj]:
                        dist[ni][nj] = nt
                        heapq.heappush(pq, (nt, ni, nj))
        return -1
# @lc code=end
