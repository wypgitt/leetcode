#
# @lc app=leetcode id=2596 lang=python3
#
# [2596] Check Knight Tour Configuration
#
# https://leetcode.com/problems/check-knight-tour-configuration/description/
#
# algorithms
# Medium (61.88%)
# Likes:    556
# Dislikes: 70
# Total Accepted:    61K
# Total Submissions: 98.6K
# Testcase Example:  "[[0,11,16,5,20],[17,4,19,10,15],[12,1,8,21,6],[3,18,23,14,9],[24,13,2,7,22]]"
#
# There is a knight on an n x n chessboard. In a valid configuration, the knight
# starts at the top-left cell of the board and visits every cell on the board
# exactly once.
#
# You are given an n x n integer matrix grid consisting of distinct integers
# from the range [0, n * n - 1] where grid[row][col] indicates that the cell
# (row, col) is the grid[row][col]^th cell that the knight visited. The moves
# are 0-indexed.
#
# Return true if grid represents a valid configuration of the knight's movements
# or false otherwise.
#
# Note that a valid knight move consists of moving two squares vertically and
# one square horizontally, or two squares horizontally and one square
# vertically. The figure below illustrates all the possible eight moves of a
# knight from some cell.
#
#
#
# Example 1:
#
# Input: grid =
# [[0,11,16,5,20],[17,4,19,10,15],[12,1,8,21,6],[3,18,23,14,9],[24,13,2,7,22]]
# Output: true
# Explanation: The above diagram represents the grid. It can be shown that it is
# a valid configuration.
#
# Example 2:
#
# Input: grid = [[0,3,6],[5,8,1],[2,7,4]]
# Output: false
# Explanation: The above diagram represents the grid. The 8^th move of the
# knight is not valid considering its position after the 7^th move.
#
#
#
# Constraints:
#
#
# n == grid.length == grid[i].length
#
#
# 3 <= n <= 7
#
#
# 0 <= grid[row][col] < n * n
#
#
# All integers in grid are unique.
#

# @lc code=start
from typing import List


class Solution:
    def checkValidGrid(self, grid: List[List[int]]) -> bool:
        """
        Interview explanation:
        Verify a knight's tour on an n x n board starting at (0,0) visiting 0..n^2-1 in order.

        Algorithm:
        - Map each step number to coordinates; check each consecutive move is a knight move
          and grid[0][0]==0.

        Complexity: O(n^2) time, O(n^2) space.
        """
        n = len(grid)
        if grid[0][0] != 0:
            return False
        pos = [None] * (n * n)
        for i in range(n):
            for j in range(n):
                pos[grid[i][j]] = (i, j)
        knight = {(1, 2), (1, -2), (-1, 2), (-1, -2), (2, 1), (2, -1), (-2, 1), (-2, -1)}
        for step in range(1, n * n):
            r1, c1 = pos[step - 1]
            r2, c2 = pos[step]
            if (r2 - r1, c2 - c1) not in knight:
                return False
        return True
# @lc code=end
