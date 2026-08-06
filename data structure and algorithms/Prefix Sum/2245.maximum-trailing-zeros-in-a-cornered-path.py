#
# @lc app=leetcode id=2245 lang=python3
#
# [2245] Maximum Trailing Zeros in a Cornered Path
#
# https://leetcode.com/problems/maximum-trailing-zeros-in-a-cornered-path/description/
#
# algorithms
# Medium (38.02%)
# Likes:    210
# Dislikes: 409
# Total Accepted:    10.2K
# Total Submissions: 26.8K
# Testcase Example:  "[[23,17,15,3,20],[8,1,20,27,11],[9,4,6,2,21],[40,9,1,10,6],[22,7,4,5,3]]"
#
# You are given a 2D integer array grid of size m x n, where each cell contains
# a positive integer.
#
# A cornered path is defined as a set of adjacent cells with at most one turn.
# More specifically, the path should exclusively move either horizontally or
# vertically up to the turn (if there is one), without returning to a previously
# visited cell. After the turn, the path will then move exclusively in the
# alternate direction: move vertically if it moved horizontally, and vice versa,
# also without returning to a previously visited cell.
#
# The product of a path is defined as the product of all the values in the path.
#
# Return the maximum number of trailing zeros in the product of a cornered path
# found in grid.
#
# Note:
#
#
# Horizontal movement means moving in either the left or right direction.
#
#
# Vertical movement means moving in either the up or down direction.
#
#
#
# Example 1:
#
# Input: grid =
# [[23,17,15,3,20],[8,1,20,27,11],[9,4,6,2,21],[40,9,1,10,6],[22,7,4,5,3]]
# Output: 3
# Explanation: The grid on the left shows a valid cornered path.
# It has a product of 15 * 20 * 6 * 1 * 10 = 18000 which has 3 trailing zeros.
# It can be shown that this is the maximum trailing zeros in the product of a
# cornered path.
#
# The grid in the middle is not a cornered path as it has more than one turn.
# The grid on the right is not a cornered path as it requires a return to a
# previously visited cell.
#
# Example 2:
#
# Input: grid = [[4,3,2],[7,6,1],[8,8,8]]
# Output: 0
# Explanation: The grid is shown in the figure above.
# There are no cornered paths in the grid that result in a product with a
# trailing zero.
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
# 1 <= m, n <= 10^5
#
#
# 1 <= m * n <= 10^5
#
#
# 1 <= grid[i][j] <= 1000
#

# @lc code=start
from typing import List


class Solution:
    def maxTrailingZeros(self, grid: List[List[int]]) -> int:
        """
        Interview explanation:
        Path goes only horizontally then vertically (L-shape / corner path), or
        vice versa. Product of cells; maximize trailing zeros (min factors of 2,5).

        Algorithm:
        - Factor each cell into (c2,c5). Prefix sums of 2s and 5s on rows left/
          right and cols up/down. For each corner cell, try 4 L orientations;
          zeros = min(sum2,sum5).

        Complexity: O(mn) time and space.
        """
        m, n = len(grid), len(grid[0])

        def factors(x: int):
            twos = fives = 0
            while x % 2 == 0:
                twos += 1
                x //= 2
            while x % 5 == 0:
                fives += 1
                x //= 5
            return twos, fives

        a2 = [[0] * n for _ in range(m)]
        a5 = [[0] * n for _ in range(m)]
        for i in range(m):
            for j in range(n):
                a2[i][j], a5[i][j] = factors(grid[i][j])

        # left[i][j] = sum on row i from 0..j inclusive
        left2 = [[0] * n for _ in range(m)]
        left5 = [[0] * n for _ in range(m)]
        right2 = [[0] * n for _ in range(m)]
        right5 = [[0] * n for _ in range(m)]
        up2 = [[0] * n for _ in range(m)]
        up5 = [[0] * n for _ in range(m)]
        down2 = [[0] * n for _ in range(m)]
        down5 = [[0] * n for _ in range(m)]

        for i in range(m):
            for j in range(n):
                left2[i][j] = a2[i][j] + (left2[i][j - 1] if j else 0)
                left5[i][j] = a5[i][j] + (left5[i][j - 1] if j else 0)
            for j in range(n - 1, -1, -1):
                right2[i][j] = a2[i][j] + (right2[i][j + 1] if j + 1 < n else 0)
                right5[i][j] = a5[i][j] + (right5[i][j + 1] if j + 1 < n else 0)
        for j in range(n):
            for i in range(m):
                up2[i][j] = a2[i][j] + (up2[i - 1][j] if i else 0)
                up5[i][j] = a5[i][j] + (up5[i - 1][j] if i else 0)
            for i in range(m - 1, -1, -1):
                down2[i][j] = a2[i][j] + (down2[i + 1][j] if i + 1 < m else 0)
                down5[i][j] = a5[i][j] + (down5[i + 1][j] if i + 1 < m else 0)

        ans = 0
        for i in range(m):
            for j in range(n):
                # corner at (i,j); subtract double-counted cell
                cands = [
                    (left2[i][j] + up2[i][j] - a2[i][j], left5[i][j] + up5[i][j] - a5[i][j]),
                    (left2[i][j] + down2[i][j] - a2[i][j], left5[i][j] + down5[i][j] - a5[i][j]),
                    (right2[i][j] + up2[i][j] - a2[i][j], right5[i][j] + up5[i][j] - a5[i][j]),
                    (right2[i][j] + down2[i][j] - a2[i][j], right5[i][j] + down5[i][j] - a5[i][j]),
                ]
                for tw, fv in cands:
                    ans = max(ans, min(tw, fv))
        return ans
# @lc code=end
