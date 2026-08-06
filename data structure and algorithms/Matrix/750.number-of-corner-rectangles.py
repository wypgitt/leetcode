#
# @lc app=leetcode id=750 lang=python3
#
# [750] Number Of Corner Rectangles
#
# https://leetcode.com/problems/number-of-corner-rectangles/description/
#
# algorithms
# Medium (67.89%)
# Likes:    633
# Dislikes: 92
# Total Accepted:    40.4K
# Total Submissions: 59.6K
# Testcase Example:  "[[1,0,0,1,0],[0,0,1,0,1],[0,0,0,1,0],[1,0,1,0,1]]"
#
#
# Given an m x n integer matrix grid where each entry is only 0 or 1,
# return the number of corner rectangles.
#
# A corner rectangle is four distinct 1's on the grid that forms an
# axis-aligned rectangle. Note that only the corners need to have the
# value 1. Also, all four 1's used must be distinct.
#
# Example 1:
#
# Input: grid = [[1,0,0,1,0],[0,0,1,0,1],[0,0,0,1,0],[1,0,1,0,1]]
# Output: 1
# Explanation: There is only one corner rectangle, with corners
# grid[1][2], grid[1][4], grid[3][2], grid[3][4].
#
# Example 2:
#
# Input: grid = [[1,1,1],[1,1,1],[1,1,1]]
# Output: 9
# Explanation: There are four 2x2 rectangles, four 2x3 and 3x2 rectangles,
# and one 3x3 rectangle.
#
# Example 3:
#
# Input: grid = [[1,1,1,1]]
# Output: 0
# Explanation: Rectangles must have four distinct corners.
#
# Constraints:
#
# m == grid.length
#
# n == grid[i].length
#
# 1 <= m, n <= 200
#
# grid[i][j] is either 0 or 1.
#
# The number of 1's in the grid is in the range [1, 6000].
#
# @lc code=start
from typing import List


class Solution:
    def countCornerRectangles(self, grid: List[List[int]]) -> int:
        """
        Interview explanation:
        Premium. A corner rectangle is an axis-aligned rectangle whose four
        corners are 1. For every pair of rows, count columns where both rows
        have 1; each pair of such columns forms a rectangle: C(count, 2).

        Algorithm:
        - ans = 0
        - For i in rows: for j in i+1..: cnt = columns c with grid[i][c]=grid[j][c]=1
          ans += cnt * (cnt - 1) // 2

        Complexity: O(R^2 * C) time, O(1) extra space.
        """
        m = len(grid)
        if m == 0:
            return 0
        n = len(grid[0])
        ans = 0
        for i in range(m):
            for j in range(i + 1, m):
                cnt = 0
                for c in range(n):
                    if grid[i][c] and grid[j][c]:
                        cnt += 1
                ans += cnt * (cnt - 1) // 2
        return ans
# @lc code=end

