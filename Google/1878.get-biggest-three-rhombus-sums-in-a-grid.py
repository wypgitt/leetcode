#
# @lc app=leetcode id=1878 lang=python3
#
# [1878] Get Biggest Three Rhombus Sums in a Grid
#
# https://leetcode.com/problems/get-biggest-three-rhombus-sums-in-a-grid/description/
#
# algorithms
# Medium (71.33%)
# Likes:    480
# Dislikes: 604
# Total Accepted:    89.9K
# Total Submissions: 126K
# Testcase Example:  "[[3,4,5,1,3],[3,3,4,2,3],[20,30,200,40,10],[1,5,5,4,1],[4,3,2,2,5]]"
#
# You are given an m x n integer matrix grid.
#
# A rhombus sum is the sum of the elements that form the border of a regular
# rhombus shape in grid. The rhombus must have the shape of a square rotated 45
# degrees with each of the corners centered in a grid cell. Below is an image
# of four valid rhombus shapes with the corresponding colored cells that should
# be included in each rhombus sum:
#
# Note that the rhombus can have an area of 0, which is depicted by the purple
# rhombus in the bottom right corner.
#
# Return the biggest three distinct rhombus sums in the grid in descending
# order. If there are less than three distinct values, return all of them.
#
# Example 1:
#
# Input: grid =
# [[3,4,5,1,3],[3,3,4,2,3],[20,30,200,40,10],[1,5,5,4,1],[4,3,2,2,5]]
# Output: [228,216,211]
# Explanation: The rhombus shapes for the three biggest distinct rhombus sums
# are depicted above.
# - Blue: 20 + 3 + 200 + 5 = 228
# - Red: 200 + 2 + 10 + 4 = 216
# - Green: 5 + 200 + 4 + 2 = 211
#
# Example 2:
#
# Input: grid = [[1,2,3],[4,5,6],[7,8,9]]
# Output: [20,9,8]
# Explanation: The rhombus shapes for the three biggest distinct rhombus sums
# are depicted above.
# - Blue: 4 + 2 + 6 + 8 = 20
# - Red: 9 (area 0 rhombus in the bottom right corner)
# - Green: 8 (area 0 rhombus in the bottom middle)
#
# Example 3:
#
# Input: grid = [[7,7,7]]
# Output: [7]
# Explanation: All three possible rhombus sums are the same, so return [7].
#
# Constraints:
#
# m == grid.length
#
# n == grid[i].length
#
# 1 <= m, n <= 50
#
# 1 <= grid[i][j] <= 10^5
#

# @lc code=start
from typing import List


class Solution:
    def getBiggestThree(self, grid: List[List[int]]) -> List[int]:
        """
        Interview explanation:
        Find up to 3 largest unique rhombus sums (k=1 is a single cell). Enumerate
        each top cell and half-diagonal length; sum the four borders once.

        Algorithm:
        - Add all cells as 1×1 rhombi.
        - For top (i,j) and l≥1: corners top, right(i+l,j+l), bottom(i+2l,j),
          left(i+l,j-l). Sum four edges without double-counting corners.
        - Return up to 3 unique sums descending.

        Complexity: O(m*n*min(m,n)) time, O(m*n) space.
        """
        m, n = len(grid), len(grid[0])
        sums = set()
        for i in range(m):
            for j in range(n):
                sums.add(grid[i][j])
        for i in range(m):
            for j in range(n):
                for l in range(1, min(m, n)):
                    r_r, c_r = i + l, j + l
                    r_b, c_b = i + 2 * l, j
                    r_l, c_l = i + l, j - l
                    if r_b >= m or c_r >= n or c_l < 0:
                        break
                    s = grid[i][j] + grid[r_r][c_r] + grid[r_b][c_b] + grid[r_l][c_l]
                    # edges without corners
                    for t in range(1, l):
                        s += grid[i + t][j + t]  # top->right
                        s += grid[i + l + t][j + l - t]  # right->bottom
                        s += grid[i + 2 * l - t][j - t]  # bottom->left
                        s += grid[i + l - t][j - l + t]  # left->top
                    sums.add(s)
        return sorted(sums, reverse=True)[:3]
# @lc code=end
