#
# @lc app=leetcode id=2711 lang=python3
#
# [2711] Difference of Number of Distinct Values on Diagonals
#
# https://leetcode.com/problems/difference-of-number-of-distinct-values-on-diagonals/description/
#
# algorithms
# Medium (68.61%)
# Likes:    144
# Dislikes: 211
# Total Accepted:    23.3K
# Total Submissions: 33.9K
# Testcase Example:  "[[1,2,3],[3,1,5],[3,2,1]]"
#
# Given a 2D grid of size m x n, you should find the matrix answer of size m x
# n.
#
# The cell answer[r][c] is calculated by looking at the diagonal values of the
# cell grid[r][c]:
#
#
# Let leftAbove[r][c] be the number of distinct values on the diagonal to the
# left and above the cell grid[r][c] not including the cell grid[r][c] itself.
#
#
# Let rightBelow[r][c] be the number of distinct values on the diagonal to the
# right and below the cell grid[r][c], not including the cell grid[r][c] itself.
#
#
# Then answer[r][c] = |leftAbove[r][c] - rightBelow[r][c]|.
#
# A matrix diagonal is a diagonal line of cells starting from some cell in
# either the topmost row or leftmost column and going in the bottom-right
# direction until the end of the matrix is reached.
#
#
# For example, in the below diagram the diagonal is highlighted using the cell
# with indices (2, 3) colored gray:
#
#
#
#
# Red-colored cells are left and above the cell.
#
#
# Blue-colored cells are right and below the cell.
#
#
#
#
#
# Return the matrix answer.
#
#
#
# Example 1:
#
# Input: grid = [[1,2,3],[3,1,5],[3,2,1]]
#
# Output: Output: [[1,1,0],[1,0,1],[0,1,1]]
#
# Explanation:
#
# To calculate the answer cells:
#
#
#
#
#                         answer
#                         left-above elements
#                         leftAbove
#                         right-below elements
#                         rightBelow
#                         |leftAbove - rightBelow|
#
#
#
#
#
#
#                         [0][0]
#                         []
#                         0
#                         [grid[1][1], grid[2][2]]
#                         |{1, 1}| = 1
#                         1
#
#
#
#
#                         [0][1]
#                         []
#                         0
#                         [grid[1][2]]
#                         |{5}| = 1
#                         1
#
#
#
#
#                         [0][2]
#                         []
#                         0
#                         []
#                         0
#                         0
#
#
#
#
#                         [1][0]
#                         []
#                         0
#                         [grid[2][1]]
#                         |{2}| = 1
#                         1
#
#
#
#
#                         [1][1]
#                         [grid[0][0]]
#                         |{1}| = 1
#                         [grid[2][2]]
#                         |{1}| = 1
#                         0
#
#
#
#
#                         [1][2]
#                         [grid[0][1]]
#                         |{2}| = 1
#                         []
#                         0
#                         1
#
#
#
#
#                         [2][0]
#                         []
#                         0
#                         []
#                         0
#                         0
#
#
#
#
#                         [2][1]
#                         [grid[1][0]]
#                         |{3}| = 1
#                         []
#                         0
#                         1
#
#
#
#
#                         [2][2]
#                         [grid[0][0], grid[1][1]]
#                         |{1, 1}| = 1
#                         []
#                         0
#                         1
#
#
#
#
# Example 2:
#
# Input: grid = [[1]]
#
# Output: Output: [[0]]
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
# 1 <= m, n, grid[i][j] <= 50
#

# @lc code=start
from typing import List


class Solution:
    def differenceOfDistinctValues(self, grid: List[List[int]]) -> List[List[int]]:
        """
        Interview explanation:
        answer[i][j] = |#distinct on top-left diagonal - #distinct on bottom-right diagonal|.

        Algorithm:
        - For each cell, scan TL diagonal into a set and BR diagonal into a set; take abs diff.
          (m,n small enough; can also precompute prefix sets along diagonals.)

        Complexity: O(mn * min(m,n)) time, O(mn) space.
        """
        m, n = len(grid), len(grid[0])
        ans = [[0] * n for _ in range(m)]
        for i in range(m):
            for j in range(n):
                left = set()
                r, c = i - 1, j - 1
                while r >= 0 and c >= 0:
                    left.add(grid[r][c])
                    r -= 1
                    c -= 1
                right = set()
                r, c = i + 1, j + 1
                while r < m and c < n:
                    right.add(grid[r][c])
                    r += 1
                    c += 1
                ans[i][j] = abs(len(left) - len(right))
        return ans
# @lc code=end
