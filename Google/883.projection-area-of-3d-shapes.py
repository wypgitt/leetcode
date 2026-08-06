#
# @lc app=leetcode id=883 lang=python3
#
# [883] Projection Area of 3D Shapes
#
# https://leetcode.com/problems/projection-area-of-3d-shapes/description/
#
# algorithms
# Easy (76.44%)
# Likes:    645
# Dislikes: 1452
# Total Accepted:    80.7K
# Total Submissions: 106K
# Testcase Example:  "[[1,2],[3,4]]"
#
# You are given an n x n grid where we place some 1 x 1 x 1 cubes that are
# axis-aligned with the x, y, and z axes.
#
# Each value v = grid[i][j] represents a tower of v cubes placed on top of the
# cell (i, j).
#
# We view the projection of these cubes onto the xy, yz, and zx planes.
#
# A projection is like a shadow, that maps our 3-dimensional figure to a
# 2-dimensional plane. We are viewing the "shadow" when looking at the cubes
# from the top, the front, and the side.
#
# Return the total area of all three projections.
#
# Example 1:
#
# Input: grid = [[1,2],[3,4]]
# Output: 17
# Explanation: Here are the three projections ("shadows") of the shape made
# with each axis-aligned plane.
#
# Example 2:
#
# Input: grid = [[2]]
# Output: 5
#
# Example 3:
#
# Input: grid = [[1,0],[0,2]]
# Output: 8
#
# Constraints:
#
# n == grid.length == grid[i].length
#
# 1 <= n <= 50
#
# 0 <= grid[i][j] <= 50
#

# @lc code=start
from typing import List


class Solution:
    def projectionArea(self, grid: List[List[int]]) -> int:
        """
        Interview explanation:
        xy projection = # nonzero cells; xz = sum of row maxima; yz = sum of
        column maxima.

        Algorithm:
        - xy = count grid[i][j]>0; xz = sum max(row); yz = sum max(col).

        Complexity: O(n^2) time, O(1) space.
        """
        n = len(grid)
        xy = sum(1 for i in range(n) for j in range(n) if grid[i][j] > 0)
        xz = sum(max(row) for row in grid)
        yz = sum(max(grid[i][j] for i in range(n)) for j in range(n))
        return xy + xz + yz
# @lc code=end

