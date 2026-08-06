#
# @lc app=leetcode id=2556 lang=python3
#
# [2556] Disconnect Path in a Binary Matrix by at Most One Flip
#
# https://leetcode.com/problems/disconnect-path-in-a-binary-matrix-by-at-most-one-flip/description/
#
# algorithms
# Medium (28.10%)
# Likes:    651
# Dislikes: 33
# Total Accepted:    19.7K
# Total Submissions: 70K
# Testcase Example:  "[[1,1,1],[1,0,0],[1,1,1]]"
#
# You are given a 0-indexed m x n binary matrix grid. You can move from a cell
# (row, col) to any of the cells (row + 1, col) or (row, col + 1) that has the
# value 1. The matrix is disconnected if there is no path from (0, 0) to (m - 1,
# n - 1).
#
# You can flip the value of at most one (possibly none) cell. You cannot flip
# the cells (0, 0) and (m - 1, n - 1).
#
# Return true if it is possible to make the matrix disconnect or false
# otherwise.
#
# Note that flipping a cell changes its value from 0 to 1 or from 1 to 0.
#
#
#
# Example 1:
#
# Input: grid = [[1,1,1],[1,0,0],[1,1,1]]
# Output: true
# Explanation: We can change the cell shown in the diagram above. There is no
# path from (0, 0) to (2, 2) in the resulting grid.
#
# Example 2:
#
# Input: grid = [[1,1,1],[1,0,1],[1,1,1]]
# Output: false
# Explanation: It is not possible to change at most one cell such that there is
# not path from (0, 0) to (2, 2).
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
# 1 <= m, n <= 1000
#
#
# 1 <= m * n <= 10^5
#
#
# grid[i][j] is either 0 or 1.
#
#
# grid[0][0] == grid[m - 1][n - 1] == 1
#

# @lc code=start
from typing import List


class Solution:
    def isPossibleToCutPath(self, grid: List[List[int]]) -> bool:
        """
        Interview explanation:
        Check if we can disconnect (0,0) from (m-1,n-1) by flipping at most one 1 to 0
        (not the two corners). Equivalent to: after removing one path, no second path remains,
        or there is a cut vertex / no two edge-disjoint paths in a grid with only right/down.

        Algorithm:
        - DFS/BFS mark one path from start to end, zeroing visited cells (except end).
        - Then check if a second path still exists; if not, a single flip (or already blocked) works.
        - First DFS from start clearing cells on a path; second DFS checks reachability.

        Complexity: O(mn) time and space.
        """
        m, n = len(grid), len(grid[0])

        def dfs(i: int, j: int) -> bool:
            if i >= m or j >= n or grid[i][j] == 0:
                return False
            if i == m - 1 and j == n - 1:
                return True
            grid[i][j] = 0
            if dfs(i + 1, j) or dfs(i, j + 1):
                return True
            return False

        # Clear one path (cells become 0). If no path exists initially, already cut.
        if not dfs(0, 0):
            return True
        grid[0][0] = 1  # restore start for second search
        return not dfs(0, 0)
# @lc code=end
