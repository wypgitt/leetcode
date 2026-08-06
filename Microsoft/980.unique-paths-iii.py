#
# @lc app=leetcode id=980 lang=python3
#
# [980] Unique Paths III
#
# https://leetcode.com/problems/unique-paths-iii/description/
#
# algorithms
# Hard (82.94%)
# Likes:    5535
# Dislikes: 200
# Total Accepted:    268K
# Total Submissions: 323K
# Testcase Example:  "[[1,0,0,0],[0,0,0,0],[0,0,2,-1]]"
#
# You are given an m x n integer array grid where grid[i][j] could be:
#
# 1 representing the starting square. There is exactly one starting square.
#
# 2 representing the ending square. There is exactly one ending square.
#
# 0 representing empty squares we can walk over.
#
# -1 representing obstacles that we cannot walk over.
#
# Return the number of 4-directional walks from the starting square to the
# ending square, that walk over every non-obstacle square exactly once.
#
# Example 1:
#
# Input: grid = [[1,0,0,0],[0,0,0,0],[0,0,2,-1]]
# Output: 2
# Explanation: We have the following two paths:
# 1. (0,0),(0,1),(0,2),(0,3),(1,3),(1,2),(1,1),(1,0),(2,0),(2,1),(2,2)
# 2. (0,0),(1,0),(2,0),(2,1),(1,1),(0,1),(0,2),(0,3),(1,3),(1,2),(2,2)
#
# Example 2:
#
# Input: grid = [[1,0,0,0],[0,0,0,0],[0,0,0,2]]
# Output: 4
# Explanation: We have the following four paths:
# 1. (0,0),(0,1),(0,2),(0,3),(1,3),(1,2),(1,1),(1,0),(2,0),(2,1),(2,2),(2,3)
# 2. (0,0),(0,1),(1,1),(1,0),(2,0),(2,1),(2,2),(1,2),(0,2),(0,3),(1,3),(2,3)
# 3. (0,0),(1,0),(2,0),(2,1),(2,2),(1,2),(1,1),(0,1),(0,2),(0,3),(1,3),(2,3)
# 4. (0,0),(1,0),(2,0),(2,1),(1,1),(0,1),(0,2),(0,3),(1,3),(1,2),(2,2),(2,3)
#
# Example 3:
#
# Input: grid = [[0,1],[2,0]]
# Output: 0
# Explanation: There is no path that walks over every empty square exactly
# once.
# Note that the starting and ending square can be anywhere in the grid.
#
# Constraints:
#
# m == grid.length
#
# n == grid[i].length
#
# 1 <= m, n <= 20
#
# 1 <= m * n <= 20
#
# -1 <= grid[i][j] <= 2
#
# There is exactly one starting cell and one ending cell.
#

# @lc code=start
from typing import List


class Solution:
    def uniquePathsIII(self, grid: List[List[int]]) -> int:
        """
        Interview explanation:
        Enumerate Hamiltonian paths on the empty cells: DFS from start, mark
        visited, recurse to 4 neighbors, unmark (backtrack). Count paths that
        reach the end after visiting every non-obstacle cell.

        Algorithm (DFS backtrack):
        - Count empty cells (0) + start; find start (sr,sc).
        - dfs(r,c,remain): if grid==2 return 1 iff remain==0; else for neighbors
          that are walkable and unvisited: mark, recurse remain-1, unmark.
        - Call dfs(start, empty_count) (start counts as visited).

        Complexity: O(3^{mn}) time worst (branching), O(mn) space (recursion).
        """
        m, n = len(grid), len(grid[0])
        empty = 0
        sr = sc = 0
        for i in range(m):
            for j in range(n):
                if grid[i][j] != -1:
                    empty += 1
                if grid[i][j] == 1:
                    sr, sc = i, j

        def dfs(r: int, c: int, remain: int) -> int:
            if grid[r][c] == 2:
                return 1 if remain == 0 else 0
            tmp = grid[r][c]
            grid[r][c] = -1
            ans = 0
            for nr, nc in ((r - 1, c), (r + 1, c), (r, c - 1), (r, c + 1)):
                if 0 <= nr < m and 0 <= nc < n and grid[nr][nc] != -1:
                    ans += dfs(nr, nc, remain - 1)
            grid[r][c] = tmp
            return ans

        return dfs(sr, sc, empty - 1)
# @lc code=end
