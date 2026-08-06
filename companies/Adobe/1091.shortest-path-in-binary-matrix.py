#
# @lc app=leetcode id=1091 lang=python3
#
# [1091] Shortest Path in Binary Matrix
#
# https://leetcode.com/problems/shortest-path-in-binary-matrix/description/
#
# algorithms
# Medium (51.99%)
# Likes:    7547
# Dislikes: 278
# Total Accepted:    894K
# Total Submissions: 1.7M
# Testcase Example:  "[[0,1],[1,0]]"
#
# Given an n x n binary matrix grid, return the length of the shortest clear
# path in the matrix. If there is no clear path, return -1.
#
# A clear path in a binary matrix is a path from the top-left cell (i.e., (0,
# 0)) to the bottom-right cell (i.e., (n - 1, n - 1)) such that:
#
# All the visited cells of the path are 0.
#
# All the adjacent cells of the path are 8-directionally connected (i.e., they
# are different and they share an edge or a corner).
#
# The length of a clear path is the number of visited cells of this path.
#
# Example 1:
#
# Input: grid = [[0,1],[1,0]]
# Output: 2
#
# Example 2:
#
# Input: grid = [[0,0,0],[1,1,0],[1,1,0]]
# Output: 4
#
# Example 3:
#
# Input: grid = [[1,0,0],[1,1,0],[1,1,0]]
# Output: -1
#
# Constraints:
#
# n == grid.length
#
# n == grid[i].length
#
# 1 <= n <= 100
#
# grid[i][j] is 0 or 1
#

# @lc code=start
from typing import List
from collections import deque


class Solution:
    def shortestPathBinaryMatrix(self, grid: List[List[int]]) -> int:
        """
        Interview explanation:
        Unweighted shortest clear path on an 8-connected grid → BFS from (0,0)
        if open, counting cells until (n-1,n-1).

        Algorithm (BFS):
        - If grid[0][0] or grid[n-1][n-1] blocked: -1.
        - Queue (r,c,dist); mark visited; explore 8 neighbors that are 0.

        Complexity: O(n²) time and space.
        """
        n = len(grid)
        if grid[0][0] or grid[n - 1][n - 1]:
            return -1
        if n == 1:
            return 1
        q = deque([(0, 0, 1)])
        grid[0][0] = 1
        dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 1), (1, -1), (1, 0), (1, 1)]
        while q:
            r, c, d = q.popleft()
            for dr, dc in dirs:
                nr, nc = r + dr, c + dc
                if 0 <= nr < n and 0 <= nc < n and grid[nr][nc] == 0:
                    if nr == n - 1 and nc == n - 1:
                        return d + 1
                    grid[nr][nc] = 1
                    q.append((nr, nc, d + 1))
        return -1
# @lc code=end
