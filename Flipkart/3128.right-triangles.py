#
# @lc app=leetcode id=3128 lang=python3
#
# [3128] Right Triangles
#
# https://leetcode.com/problems/right-triangles/description/
#
# algorithms
# Medium (48.87%)
# Likes:    137
# Dislikes: 24
# Total Accepted:    24.7K
# Total Submissions: 50.5K
# Testcase Example:  "[[0,1,0],[0,1,1],[0,1,0]]"
#
#
# You are given a 2D boolean matrix grid.
#
# A collection of 3 elements of grid is a right triangle if one of its
# elements is in the same row with another element and in the same column
# with the third element. The 3 elements may not be next to each other.
#
# Return an integer that is the number of right triangles that can be made
# with 3 elements of grid such that all of them have a value of 1.
#
# Example 1:
#
#                         0
#                         1
#                         0
#
#                         0
#                         1
#                         1
#
#                         0
#                         1
#                         0
#
#                         0
#                         1
#                         0
#
#                         0
#                         1
#                         1
#
#                         0
#                         1
#                         0
#
#                         0
#                         1
#                         0
#
#                         0
#                         1
#                         1
#
#                         0
#                         1
#                         0
#
# Input: grid = [[0,1,0],[0,1,1],[0,1,0]]
#
# Output: 2
#
# Explanation:
#
# There are two right triangles with elements of the value 1. Notice that
# the blue ones do not form a right triangle because the 3 elements are in
# the same column.
#
# Example 2:
#
#                         1
#                         0
#                         0
#                         0
#
#                         0
#                         1
#                         0
#                         1
#
#                         1
#                         0
#                         0
#                         0
#
# Input: grid = [[1,0,0,0],[0,1,0,1],[1,0,0,0]]
#
# Output: 0
#
# Explanation:
#
# There are no right triangles with elements of the value 1.  Notice that
# the blue ones do not form a right triangle.
#
# Example 3:
#
#                         1
#                         0
#                         1
#
#                         1
#                         0
#                         0
#
#                         1
#                         0
#                         0
#
#                         1
#                         0
#                         1
#
#                         1
#                         0
#                         0
#
#                         1
#                         0
#                         0
#
# Input: grid = [[1,0,1],[1,0,0],[1,0,0]]
#
# Output: 2
#
# Explanation:
#
# There are two right triangles with elements of the value 1.
#
# Constraints:
#
# 1 <= grid.length <= 1000
#
# 1 <= grid[i].length <= 1000
#
# 0 <= grid[i][j] <= 1
#

# @lc code=start
from typing import List


class Solution:
    def numberOfRightTriangles(self, grid: List[List[int]]) -> int:
        """
        Interview explanation:
        Count axis-aligned right triangles of three 1-cells (right angle at a
        shared row/column corner).

        Algorithm:
        - Precompute ones per row and per column.
        - For each cell (i,j) with value 1, add (row[i]-1)*(col[j]-1): choose
          another 1 in the row and another in the column as the other vertices.

        Complexity: O(m*n) time, O(m+n) space.
        """
        m, n = len(grid), len(grid[0])
        row = [sum(r) for r in grid]
        col = [sum(grid[i][j] for i in range(m)) for j in range(n)]
        ans = 0
        for i in range(m):
            for j in range(n):
                if grid[i][j]:
                    ans += (row[i] - 1) * (col[j] - 1)
        return ans
# @lc code=end
