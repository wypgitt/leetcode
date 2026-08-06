#
# @lc app=leetcode id=2128 lang=python3
#
# [2128] Remove All Ones With Row and Column Flips
#
# https://leetcode.com/problems/remove-all-ones-with-row-and-column-flips/description/
#
# algorithms
# Medium (76.20%)
# Likes:    482
# Dislikes: 189
# Total Accepted:    34.9K
# Total Submissions: 45.8K
# Testcase Example:  "[[0,1,0],[1,0,1],[0,1,0]]"
#
#
# You are given an m x n binary matrix grid.
#
# In one operation, you can choose any row or column and flip each value
# in that row or column (i.e., changing all 0's to 1's, and all 1's to
# 0's).
#
# Return true if it is possible to remove all 1's from grid using any
# number of operations or false otherwise.
#
# Example 1:
#
# Input: grid = [[0,1,0],[1,0,1],[0,1,0]]
# Output: true
# Explanation: One possible way to remove all 1's from grid is to:
# - Flip the middle row
# - Flip the middle column
#
# Example 2:
#
# Input: grid = [[1,1,0],[0,0,0],[0,0,0]]
# Output: false
# Explanation: It is impossible to remove all 1's from grid.
#
# Example 3:
#
# Input: grid = [[0]]
# Output: true
# Explanation: There are no 1's in grid.
#
# Constraints:
#
# m == grid.length
#
# n == grid[i].length
#
# 1 <= m, n <= 300
#
# grid[i][j] is either 0 or 1.
#
# @lc code=start
from typing import List


class Solution:
    def removeOnes(self, grid: List[List[int]]) -> bool:
        """
        Interview explanation:
        Premium: flip any row or column (0↔1). Can we make the matrix all zeros?
        Equivalent: every row equals the first row or its bitwise complement.

        Algorithm:
        - Compare each row to row0 and flipped(row0).

        Complexity: O(mn) time, O(n) space.
        """
        rev = [1 - x for x in grid[0]]
        return all(row == grid[0] or row == rev for row in grid)
# @lc code=end

