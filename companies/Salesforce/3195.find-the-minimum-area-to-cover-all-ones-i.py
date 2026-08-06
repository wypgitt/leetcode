#
# @lc app=leetcode id=3195 lang=python3
#
# [3195] Find the Minimum Area to Cover All Ones I
#
# https://leetcode.com/problems/find-the-minimum-area-to-cover-all-ones-i/description/
#
# algorithms
# Medium (78.19%)
# Likes:    497
# Dislikes: 32
# Total Accepted:    168.3K
# Total Submissions: 215.3K
# Testcase Example:  "[[0,1,0],[1,0,1]]"
#
#
# You are given a 2D binary array grid. Find a rectangle with horizontal
# and vertical sides with the smallest area, such that all the 1's in grid
# lie inside this rectangle.
#
# Return the minimum possible area of the rectangle.
#
# Example 1:
#
# Input: grid = [[0,1,0],[1,0,1]]
#
# Output: 6
#
# Explanation:
#
# The smallest rectangle has a height of 2 and a width of 3, so it has an
# area of 2 * 3 = 6.
#
# Example 2:
#
# Input: grid = [[1,0],[0,0]]
#
# Output: 1
#
# Explanation:
#
# The smallest rectangle has both height and width 1, so its area is 1 * 1
# = 1.
#
# Constraints:
#
# 1 <= grid.length, grid[i].length <= 1000
#
# grid[i][j] is either 0 or 1.
#
# The input is generated such that there is at least one 1 in grid.
#

# @lc code=start

from typing import List


class Solution:
    def minimumArea(self, grid: List[List[int]]) -> int:
        """
        Interview explanation:
        Smallest axis-aligned rectangle covering all 1s is the bounding box of
        all 1 cells.

        Algorithm:
        - Track min/max row and col among cells with value 1; area = h*w.

        Complexity: O(mn) time, O(1) space.
        """
        m, n = len(grid), len(grid[0])
        r1, r2 = m, -1
        c1, c2 = n, -1
        for i in range(m):
            for j in range(n):
                if grid[i][j]:
                    r1 = min(r1, i)
                    r2 = max(r2, i)
                    c1 = min(c1, j)
                    c2 = max(c2, j)
        return (r2 - r1 + 1) * (c2 - c1 + 1)
# @lc code=end
