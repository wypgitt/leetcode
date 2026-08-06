#
# @lc app=leetcode id=329 lang=python3
#
# [329] Longest Increasing Path in a Matrix
#
# https://leetcode.com/problems/longest-increasing-path-in-a-matrix/description/
#
# algorithms
# Hard (56.91%)
# Likes:    9603
# Dislikes: 147
# Total Accepted:    740K
# Total Submissions: 1.3M
# Testcase Example:  "[[9,9,4],[6,6,8],[2,1,1]]"
#
# Given an m x n integers matrix, return the length of the longest increasing
# path in matrix.
#
# From each cell, you can either move in four directions: left, right, up, or
# down. You may not move diagonally or move outside the boundary (i.e.,
# wrap-around is not allowed).
#
# Example 1:
#
# Input: matrix = [[9,9,4],[6,6,8],[2,1,1]]
# Output: 4
# Explanation: The longest increasing path is [1, 2, 6, 9].
#
# Example 2:
#
# Input: matrix = [[3,4,5],[3,2,6],[2,2,1]]
# Output: 4
# Explanation: The longest increasing path is [3, 4, 5, 6]. Moving diagonally
# is not allowed.
#
# Example 3:
#
# Input: matrix = [[1]]
# Output: 1
#
# Constraints:
#
# m == matrix.length
#
# n == matrix[i].length
#
# 1 <= m, n <= 200
#
# 0 <= matrix[i][j] <= 2^31 - 1
#

# @lc code=start
from typing import List


class Solution:
    def longestIncreasingPath(self, matrix: List[List[int]]) -> int:
        """
        Interview explanation:
        DFS + memoization: from each cell, longest increasing path is 1 + max
        over strictly greater 4-neighbors; memoize per cell to avoid recompute.

        Algorithm:
        - memo[r][c] = longest path starting at (r,c).
        - DFS explores up/down/left/right when neighbor > current.
        - Answer is max memo over all cells.

        Complexity: O(mn) time and space.
        """
        if not matrix or not matrix[0]:
            return 0
        m, n = len(matrix), len(matrix[0])
        memo = [[0] * n for _ in range(m)]
        dirs = ((1, 0), (-1, 0), (0, 1), (0, -1))

        def dfs(r: int, c: int) -> int:
            if memo[r][c]:
                return memo[r][c]
            best = 1
            for dr, dc in dirs:
                nr, nc = r + dr, c + dc
                if 0 <= nr < m and 0 <= nc < n and matrix[nr][nc] > matrix[r][c]:
                    best = max(best, 1 + dfs(nr, nc))
            memo[r][c] = best
            return best

        return max(dfs(i, j) for i in range(m) for j in range(n))
# @lc code=end
