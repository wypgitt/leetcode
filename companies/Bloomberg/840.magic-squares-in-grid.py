#
# @lc app=leetcode id=840 lang=python3
#
# [840] Magic Squares In Grid
#
# https://leetcode.com/problems/magic-squares-in-grid/description/
#
# algorithms
# Medium (55.21%)
# Likes:    1117
# Dislikes: 1906
# Total Accepted:    231K
# Total Submissions: 419K
# Testcase Example:  "[[4,3,8,4],[9,5,1,9],[2,7,6,2]]"
#
# A 3 x 3 magic square is a 3 x 3 grid filled with distinct numbers from 1 to 9
# such that each row, column, and both diagonals all have the same sum.
#
# Given a row x col grid of integers, how many 3 x 3 magic square subgrids are
# there?
#
# Note: while a magic square can only contain numbers from 1 to 9, grid may
# contain numbers up to 15.
#
# Example 1:
#
# Input: grid = [[4,3,8,4],[9,5,1,9],[2,7,6,2]]
# Output: 1
# Explanation:
# The following subgrid is a 3 x 3 magic square:
#
# while this one is not:
#
# In total, there is only one magic square inside the given grid.
#
# Example 2:
#
# Input: grid = [[8]]
# Output: 0
#
# Constraints:
#
# row == grid.length
#
# col == grid[i].length
#
# 1 <= row, col <= 10
#
# 0 <= grid[i][j] <= 15
#

# @lc code=start

from typing import List


class Solution:
    def numMagicSquaresInside(self, grid: List[List[int]]) -> int:
        """
        Interview explanation:
        Count 3x3 subgrids that are magic: distinct 1..9 and all rows/cols/
        diagonals sum to 15. Center of a 1..9 magic square must be 5.

        Algorithm:
        - For each top-left (i,j) of 3x3, check distinct 1..9 and eight sums=15.

        Complexity: O(m*n) time, O(1) space.
        """
        m, n = len(grid), len(grid[0])
        ans = 0

        def magic(i: int, j: int) -> bool:
            vals = [grid[i + a][j + b] for a in range(3) for b in range(3)]
            if sorted(vals) != list(range(1, 10)):
                return False
            # rows, cols, diags
            for a in range(3):
                if sum(grid[i + a][j + b] for b in range(3)) != 15:
                    return False
                if sum(grid[i + b][j + a] for b in range(3)) != 15:
                    return False
            if grid[i][j] + grid[i + 1][j + 1] + grid[i + 2][j + 2] != 15:
                return False
            if grid[i][j + 2] + grid[i + 1][j + 1] + grid[i + 2][j] != 15:
                return False
            return True

        for i in range(m - 2):
            for j in range(n - 2):
                if grid[i + 1][j + 1] == 5 and magic(i, j):
                    ans += 1
        return ans
# @lc code=end
