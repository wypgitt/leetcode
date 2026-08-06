#
# @lc app=leetcode id=892 lang=python3
#
# [892] Surface Area of 3D Shapes
#
# https://leetcode.com/problems/surface-area-of-3d-shapes/description/
#
# algorithms
# Easy (71.18%)
# Likes:    614
# Dislikes: 763
# Total Accepted:    59.6K
# Total Submissions: 83.8K
# Testcase Example:  "[[1,2],[3,4]]"
#
# You are given an n x n grid where you have placed some 1 x 1 x 1 cubes. Each
# value v = grid[i][j] represents a tower of v cubes placed on top of cell (i,
# j).
#
# After placing these cubes, you have decided to glue any directly adjacent
# cubes to each other, forming several irregular 3D shapes.
#
# Return the total surface area of the resulting shapes.
#
# Note: The bottom face of each shape counts toward its surface area.
#
# Example 1:
#
# Input: grid = [[1,2],[3,4]]
# Output: 34
#
# Example 2:
#
# Input: grid = [[1,1,1],[1,0,1],[1,1,1]]
# Output: 32
#
# Example 3:
#
# Input: grid = [[2,2,2],[2,1,2],[2,2,2]]
# Output: 46
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
    def surfaceArea(self, grid: List[List[int]]) -> int:
        """
        Interview explanation:
        Each cube has 6 faces; subtract 2 per touching face (stack vertical
        and adjacent horizontal neighbors).

        Algorithm:
        - For each cell v>0: add 2 + 4*v (top/bottom + sides), then subtract
          2*min with right/down neighbors (and v*(v-1)*2 already in 4v-2(v-1)).
        - Simpler: ans=0; for each cube stack: ans += 6*v - 2*(v-1) if v;
          subtract 2*min with N/W neighbors.

        Complexity: O(n^2) time, O(1) space.
        """
        n = len(grid)
        ans = 0
        for i in range(n):
            for j in range(n):
                v = grid[i][j]
                if v:
                    ans += 4 * v + 2
                    if i > 0:
                        ans -= 2 * min(v, grid[i - 1][j])
                    if j > 0:
                        ans -= 2 * min(v, grid[i][j - 1])
        return ans
# @lc code=end

