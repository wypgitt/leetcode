#
# @lc app=leetcode id=2639 lang=python3
#
# [2639] Find the Width of Columns of a Grid
#
# https://leetcode.com/problems/find-the-width-of-columns-of-a-grid/description/
#
# algorithms
# Easy (70.56%)
# Likes:    196
# Dislikes: 56
# Total Accepted:    42.1K
# Total Submissions: 59.7K
# Testcase Example:  "[[1],[22],[333]]"
#
# You are given a 0-indexed m x n integer matrix grid. The width of a column is
# the maximum length of its integers.
#
#
# For example, if grid = [[-10], [3], [12]], the width of the only column is 3
# since -10 is of length 3.
#
# Return an integer array ans of size n where ans[i] is the width of the i^th
# column.
#
# The length of an integer x with len digits is equal to len if x is
# non-negative, and len + 1 otherwise.
#
#
#
# Example 1:
#
# Input: grid = [[1],[22],[333]]
# Output: [3]
# Explanation: In the 0^th column, 333 is of length 3.
#
# Example 2:
#
# Input: grid = [[-15,1,3],[15,7,12],[5,6,-2]]
# Output: [3,1,2]
# Explanation:
# In the 0^th column, only -15 is of length 3.
# In the 1^st column, all integers are of length 1.
# In the 2^nd column, both 12 and -2 are of length 2.
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
# 1 <= m, n <= 100
#
#
# -10^9 <= grid[r][c] <= 10^9
#

# @lc code=start
from typing import List


class Solution:
    def findColumnWidth(self, grid: List[List[int]]) -> List[int]:
        """
        Interview explanation:
        Column width is the max string length of any number in that column
        (negative sign counts as one character).

        Algorithm:
        - For each column j, take max(len(str(grid[i][j]))) over all rows.

        Complexity: O(m n) time, O(1) extra space (output excluded).
        """
        return [max(len(str(grid[i][j])) for i in range(len(grid))) for j in range(len(grid[0]))]

    def findColumnWidth_digits(self, grid: List[List[int]]) -> List[int]:
        """
        Interview explanation:
        Alternate: compute digit length without converting to string.

        Algorithm:
        - For each value, count digits via abs + loop; add 1 if negative.

        Complexity: O(m n log V) time, O(1) extra space.
        """
        def width(x: int) -> int:
            if x == 0:
                return 1
            n, v = (1, -x) if x < 0 else (0, x)
            while v:
                n += 1
                v //= 10
            return n

        m, n = len(grid), len(grid[0])
        ans = [0] * n
        for j in range(n):
            ans[j] = max(width(grid[i][j]) for i in range(m))
        return ans
# @lc code=end
