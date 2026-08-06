#
# @lc app=leetcode id=3239 lang=python3
#
# [3239] Minimum Number of Flips to Make Binary Grid Palindromic I
#
# https://leetcode.com/problems/minimum-number-of-flips-to-make-binary-grid-palindromic-i/description/
#
# algorithms
# Medium (74.28%)
# Likes:    84
# Dislikes: 10
# Total Accepted:    39.9K
# Total Submissions: 53.8K
# Testcase Example:  "[[1,0,0],[0,0,0],[0,0,1]]"
#
#
# You are given an m x n binary matrix grid.
#
# A row or column is considered palindromic if its values read the same
# forward and backward.
#
# You can flip any number of cells in grid from 0 to 1, or from 1 to 0.
#
# Return the minimum number of cells that need to be flipped to make
# either all rows palindromic or all columns palindromic.
#
# Example 1:
#
# Input: grid = [[1,0,0],[0,0,0],[0,0,1]]
#
# Output: 2
#
# Explanation:
#
# Flipping the highlighted cells makes all the rows palindromic.
#
# Example 2:
#
# Input: grid = [[0,1],[0,1],[0,0]]
#
# Output: 1
#
# Explanation:
#
# Flipping the highlighted cell makes all the columns palindromic.
#
# Example 3:
#
# Input: grid = [[1],[0]]
#
# Output: 0
#
# Explanation:
#
# All rows are already palindromic.
#
# Constraints:
#
# m == grid.length
#
# n == grid[i].length
#
# 1 <= m * n <= 2 * 10^5
#
# 0 <= grid[i][j] <= 1
#

# @lc code=start
from typing import List


class Solution:
    def minFlips(self, grid: List[List[int]]) -> int:
        """
        Interview explanation:
        We may either make every row a palindrome or every column a palindrome.
        Take the cheaper of the two independent options.

        Algorithm:
        - Rows: for each row, count mismatches of symmetric pairs; sum flips.
        - Columns: same on each column; return min(row_cost, col_cost).

        Complexity: O(m*n) time, O(1) space.
        Alternate: transpose mentally and reuse one palindrome-cost helper.
        """
        m, n = len(grid), len(grid[0])
        row_cost = 0
        for i in range(m):
            for j in range(n // 2):
                if grid[i][j] != grid[i][n - 1 - j]:
                    row_cost += 1
        col_cost = 0
        for j in range(n):
            for i in range(m // 2):
                if grid[i][j] != grid[m - 1 - i][j]:
                    col_cost += 1
        return min(row_cost, col_cost)

# @lc code=end
