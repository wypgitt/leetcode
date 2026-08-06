#
# @lc app=leetcode id=694 lang=python3
#
# [694] Number of Distinct Islands
#
# https://leetcode.com/problems/number-of-distinct-islands/description/
#
# algorithms
# Medium (62.93%)
# Likes:    2340
# Dislikes: 154
# Total Accepted:    210.6K
# Total Submissions: 334.6K
# Testcase Example:  "[[1,1,0,0,0],[1,1,0,0,0],[0,0,0,1,1],[0,0,0,1,1]]"
#
#
# You are given an m x n binary matrix grid. An island is a group of 1's
# (representing land) connected 4-directionally (horizontal or vertical.)
# You may assume all four edges of the grid are surrounded by water.
#
# An island is considered to be the same as another if and only if one
# island can be translated (and not rotated or reflected) to equal the
# other.
#
# Return the number of distinct islands.
#
# Example 1:
#
# Input: grid = [[1,1,0,0,0],[1,1,0,0,0],[0,0,0,1,1],[0,0,0,1,1]]
# Output: 1
#
# Example 2:
#
# Input: grid = [[1,1,0,1,1],[1,0,0,0,0],[0,0,0,0,1],[1,1,0,1,1]]
# Output: 3
#
# Constraints:
#
# m == grid.length
#
# n == grid[i].length
#
# 1 <= m, n <= 50
#
# grid[i][j] is either 0 or 1.
#
# @lc code=start
from typing import List


class Solution:
    def numDistinctIslands(self, grid: List[List[int]]) -> int:
        """
        Interview explanation:
        Premium: count distinct island shapes (translation-invariant). DFS and
        record the path signature relative to the start (or sequence of moves
        including backtracks).

        Algorithm:
        - For each unvisited land, DFS recording moves 'U/D/L/R' and 'B' backtrack;
          add signature string to a set.
        - Answer = size of set.

        Complexity: O(m*n) time and space.
        """
        if not grid:
            return 0
        m, n = len(grid), len(grid[0])
        shapes = set()

        def dfs(i: int, j: int, path: List[str], direction: str) -> None:
            if i < 0 or i >= m or j < 0 or j >= n or grid[i][j] == 0:
                return
            grid[i][j] = 0
            path.append(direction)
            dfs(i + 1, j, path, "D")
            dfs(i - 1, j, path, "U")
            dfs(i, j + 1, path, "R")
            dfs(i, j - 1, path, "L")
            path.append("B")

        for i in range(m):
            for j in range(n):
                if grid[i][j] == 1:
                    path: List[str] = []
                    dfs(i, j, path, "S")
                    shapes.add("".join(path))
        return len(shapes)
# @lc code=end
