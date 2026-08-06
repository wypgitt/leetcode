#
# @lc app=leetcode id=1139 lang=python3
#
# [1139] Largest 1-Bordered Square
#
# https://leetcode.com/problems/largest-1-bordered-square/description/
#
# algorithms
# Medium (52.36%)
# Likes:    772
# Dislikes: 119
# Total Accepted:    34.4K
# Total Submissions: 65.6K
# Testcase Example:  "[[1,1,1],[1,0,1],[1,1,1]]"
#
# Given a 2D grid of 0s and 1s, return the number of elements in the largest
# square subgrid that has all 1s on its border, or 0 if such a subgrid doesn't
# exist in the grid.
#
# Example 1:
#
# Input: grid = [[1,1,1],[1,0,1],[1,1,1]]
# Output: 9
#
# Example 2:
#
# Input: grid = [[1,1,0,0]]
# Output: 1
#
# Constraints:
#
# 1 <= grid.length <= 100
#
# 1 <= grid[0].length <= 100
#
# grid[i][j] is 0 or 1
#

# @lc code=start
from typing import List


class Solution:
    def largest1BorderedSquare(self, grid: List[List[int]]) -> int:
        """
        Interview explanation:
        Largest square whose border is all 1s (interior may be anything).
        Precompute consecutive 1s to the left and up; try large side lengths.

        Algorithm:
        - hor[i][j] = horizontal run of 1s ending at (i,j); ver similarly upward.
        - For each bottom-right (i,j), try side len from min(hor,ver) down;
          check top and left borders via hor/ver at the other corners.

        Complexity: O(m*n*min(m,n)) time, O(m*n) space.
        """
        m, n = len(grid), len(grid[0])
        hor = [[0] * n for _ in range(m)]
        ver = [[0] * n for _ in range(m)]
        for i in range(m):
            for j in range(n):
                if grid[i][j]:
                    hor[i][j] = (hor[i][j - 1] if j else 0) + 1
                    ver[i][j] = (ver[i - 1][j] if i else 0) + 1

        for side in range(min(m, n), 0, -1):
            for i in range(side - 1, m):
                for j in range(side - 1, n):
                    if (
                        hor[i][j] >= side
                        and ver[i][j] >= side
                        and hor[i - side + 1][j] >= side
                        and ver[i][j - side + 1] >= side
                    ):
                        return side * side
        return 0
# @lc code=end
