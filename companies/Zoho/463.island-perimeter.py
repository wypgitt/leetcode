#
# @lc app=leetcode id=463 lang=python3
#
# [463] Island Perimeter
#
# https://leetcode.com/problems/island-perimeter/description/
#
# algorithms
# Easy (74.3%)
# Likes:    7368
# Dislikes: 432
# Total Accepted:    858K
# Total Submissions: 1.2M
# Testcase Example:  "[[0,1,0,0],[1,1,1,0],[0,1,0,0],[1,1,0,0]]"
#
# You are given row x col grid representing a map where grid[i][j] = 1
# represents land and grid[i][j] = 0 represents water.
#
# Grid cells are connected horizontally/vertically (not diagonally). The grid
# is completely surrounded by water, and there is exactly one island (i.e., one
# or more connected land cells).
#
# The island doesn't have "lakes", meaning the water inside isn't connected to
# the water around the island. One cell is a square with side length 1. The
# grid is rectangular, width and height don't exceed 100. Determine the
# perimeter of the island.
#
# Example 1:
#
# Input: grid = [[0,1,0,0],[1,1,1,0],[0,1,0,0],[1,1,0,0]]
# Output: 16
# Explanation: The perimeter is the 16 yellow stripes in the image above.
#
# Example 2:
#
# Input: grid = [[1]]
# Output: 4
#
# Example 3:
#
# Input: grid = [[1,0]]
# Output: 4
#
# Constraints:
#
# row == grid.length
#
# col == grid[i].length
#
# 1 <= row, col <= 100
#
# grid[i][j] is 0 or 1.
#
# There is exactly one island in grid.
#

# @lc code=start
from typing import List


class Solution:
    def islandPerimeter(self, grid: List[List[int]]) -> int:
        """
        Interview explanation:
        Each land cell contributes 4 edges; each shared edge between two land
        cells removes 2 from the perimeter. Count lands and horizontal/vertical
        adjacencies.

        Algorithm:
        - For each land: peri += 4; if left neighbor land: peri -= 2;
          if up neighbor land: peri -= 2.

        Complexity: O(mn) time, O(1) space.
        """
        peri = 0
        rows, cols = len(grid), len(grid[0])
        for r in range(rows):
            for c in range(cols):
                if grid[r][c] == 0:
                    continue
                peri += 4
                if r > 0 and grid[r - 1][c] == 1:
                    peri -= 2
                if c > 0 and grid[r][c - 1] == 1:
                    peri -= 2
        return peri
# @lc code=end
