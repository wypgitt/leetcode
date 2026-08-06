#
# @lc app=leetcode id=1975 lang=python3
#
# [1975] Maximum Matrix Sum
#
# https://leetcode.com/problems/maximum-matrix-sum/description/
#
# algorithms
# Medium (67.51%)
# Likes:    1628
# Dislikes: 75
# Total Accepted:    240K
# Total Submissions: 355K
# Testcase Example:  "[[1,-1],[-1,1]]"
#
# You are given an n x n integer matrix. You can do the following operation any
# number of times:
#
# Choose any two adjacent elements of matrix and multiply each of them by -1.
#
# Two elements are considered adjacent if and only if they share a border.
#
# Your goal is to maximize the summation of the matrix's elements. Return the
# maximum sum of the matrix's elements using the operation mentioned above.
#
# Example 1:
#
# Input: matrix = [[1,-1],[-1,1]]
# Output: 4
# Explanation: We can follow the following steps to reach sum equals 4:
# - Multiply the 2 elements in the first row by -1.
# - Multiply the 2 elements in the first column by -1.
#
# Example 2:
#
# Input: matrix = [[1,2,3],[-1,-2,-3],[1,2,3]]
# Output: 16
# Explanation: We can follow the following step to reach sum equals 16:
# - Multiply the 2 last elements in the second row by -1.
#
# Constraints:
#
# n == matrix.length == matrix[i].length
#
# 2 <= n <= 250
#
# -10^5 <= matrix[i][j] <= 10^5
#

# @lc code=start
from typing import List


class Solution:
    def maxMatrixSum(self, matrix: List[List[int]]) -> int:
        """
        Interview explanation:
        You may flip signs of adjacent pairs any times. Negatives can be paired
        away; if odd count of negatives, one negative remains — make it the
        smallest absolute value. Answer = sum(|x|) - 2*min|x| if odd else sum(|x|).

        Algorithm:
        - Track total abs sum, min abs, and negative count parity.

        Complexity: O(n^2) time, O(1) space.
        """
        total = 0
        neg = 0
        mn = 10**18
        for row in matrix:
            for x in row:
                if x < 0:
                    neg += 1
                ax = abs(x)
                total += ax
                mn = min(mn, ax)
        if neg % 2:
            return total - 2 * mn
        return total

    def maxMatrixSum_flat(self, matrix: List[List[int]]) -> int:
        """
        Interview explanation:
        Alternate: flatten values; same parity argument on negatives.

        Algorithm:
        - vals = all cells; same sum(abs)-2*min if odd negatives.

        Complexity: O(n^2) time, O(n^2) space.
        """
        vals = [x for row in matrix for x in row]
        total = sum(abs(x) for x in vals)
        if sum(x < 0 for x in vals) % 2 == 0:
            return total
        return total - 2 * min(abs(x) for x in vals)
# @lc code=end

