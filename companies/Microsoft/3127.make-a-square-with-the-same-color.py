#
# @lc app=leetcode id=3127 lang=python3
#
# [3127] Make a Square with the Same Color
#
# https://leetcode.com/problems/make-a-square-with-the-same-color/description/
#
# algorithms
# Easy (52.95%)
# Likes:    95
# Dislikes: 12
# Total Accepted:    35.2K
# Total Submissions: 66.5K
# Testcase Example:  "[[\"B\",\"W\",\"B\"],[\"B\",\"W\",\"W\"],[\"B\",\"W\",\"B\"]]"
#
#
# You are given a 2D matrix grid of size 3 x 3 consisting only of
# characters 'B' and 'W'. Character 'W' represents the white color, and
# character 'B' represents the black color.
#
# Your task is to change the color of at most one cell so that the matrix
# has a 2 x 2 square where all cells are of the same color.
#
# Return true if it is possible to create a 2 x 2 square of the same
# color, otherwise, return false.
#
# Example 1:
#
# Input: grid = [["B","W","B"],["B","W","W"],["B","W","B"]]
#
# Output: true
#
# Explanation:
#
# It can be done by changing the color of the grid[0][2].
#
# Example 2:
#
# Input: grid = [["B","W","B"],["W","B","W"],["B","W","B"]]
#
# Output: false
#
# Explanation:
#
# It cannot be done by changing at most one cell.
#
# Example 3:
#
# Input: grid = [["B","W","B"],["B","W","W"],["B","W","W"]]
#
# Output: true
#
# Explanation:
#
# The grid already contains a 2 x 2 square of the same color.
#
# Constraints:
#
# grid.length == 3
#
# grid[i].length == 3
#
# grid[i][j] is either 'W' or 'B'.
#

# @lc code=start
from typing import List


class Solution:
    def canMakeSquare(self, grid: List[List[str]]) -> bool:
        """
        Interview explanation:
        3x3 board of 'B'/'W'. After changing at most one cell, some 2x2 block
        should be monochrome.

        Algorithm:
        - For each of the four 2x2 blocks, count 'B'. If count is 0,1,3, or 4,
          at most one flip makes it uniform (already uniform or one minority).

        Complexity: O(1) time, O(1) space.
        """
        for i in range(2):
            for j in range(2):
                black = sum(
                    grid[i + di][j + dj] == "B"
                    for di in range(2)
                    for dj in range(2)
                )
                if black != 2:
                    return True
        return False
# @lc code=end
