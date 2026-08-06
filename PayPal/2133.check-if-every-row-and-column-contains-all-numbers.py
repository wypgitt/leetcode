#
# @lc app=leetcode id=2133 lang=python3
#
# [2133] Check if Every Row and Column Contains All Numbers
#
# https://leetcode.com/problems/check-if-every-row-and-column-contains-all-numbers/description/
#
# algorithms
# Easy (54.26%)
# Likes:    1100
# Dislikes: 58
# Total Accepted:    121K
# Total Submissions: 223K
# Testcase Example:  "[[1,2,3],[3,1,2],[2,3,1]]"
#
# An n x n matrix is valid if every row and every column contains all the
# integers from 1 to n (inclusive).
#
# Given an n x n integer matrix matrix, return true if the matrix is valid.
# Otherwise, return false.
#
#
#
# Example 1:
#
# Input: matrix = [[1,2,3],[3,1,2],[2,3,1]]
# Output: true
# Explanation: In this case, n = 3, and every row and column contains the
# numbers 1, 2, and 3.
# Hence, we return true.
#
# Example 2:
#
# Input: matrix = [[1,1,1],[1,2,3],[1,2,3]]
# Output: false
# Explanation: In this case, n = 3, but the first row and the first column do
# not contain the numbers 2 or 3.
# Hence, we return false.
#
#
#
# Constraints:
#
#
# n == matrix.length == matrix[i].length
#
#
# 1 <= n <= 100
#
#
# 1 <= matrix[i][j] <= n
#


# @lc code=start
from typing import List


class Solution:
    def checkValid(self, matrix: List[List[int]]) -> bool:
        """
        Interview explanation:
        n×n matrix valid if every row and column is a permutation of 1..n.

        Algorithm:
        - For each row/col, check set size == n (values in 1..n implied by constraints).

        Complexity: O(n^2) time, O(n) space.
        """
        n = len(matrix)
        for i in range(n):
            if len(set(matrix[i])) != n:
                return False
            if len({matrix[r][i] for r in range(n)}) != n:
                return False
        return True
# @lc code=end

