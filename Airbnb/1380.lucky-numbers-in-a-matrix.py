#
# @lc app=leetcode id=1380 lang=python3
#
# [1380] Lucky Numbers in a Matrix
#
# https://leetcode.com/problems/lucky-numbers-in-a-matrix/description/
#
# algorithms
# Easy (80.18%)
# Likes:    2375
# Dislikes: 123
# Total Accepted:    308K
# Total Submissions: 384K
# Testcase Example:  "[[3,7,8],[9,11,13],[15,16,17]]"
#
# Given an m x n matrix of distinct numbers, return all lucky numbers in the
# matrix in any order.
#
# A lucky number is an element of the matrix such that it is the minimum
# element in its row and maximum in its column.
#
# Example 1:
#
# Input: matrix = [[3,7,8],[9,11,13],[15,16,17]]
# Output: [15]
# Explanation: 15 is the only lucky number since it is the minimum in its row
# and the maximum in its column.
#
# Example 2:
#
# Input: matrix = [[1,10,4,2],[9,3,8,7],[15,16,17,12]]
# Output: [12]
# Explanation: 12 is the only lucky number since it is the minimum in its row
# and the maximum in its column.
#
# Example 3:
#
# Input: matrix = [[7,8],[1,2]]
# Output: [7]
# Explanation: 7 is the only lucky number since it is the minimum in its row
# and the maximum in its column.
#
# Constraints:
#
# m == mat.length
#
# n == mat[i].length
#
# 1 <= n, m <= 50
#
# 1 <= matrix[i][j] <= 10^5.
#
# All elements in the matrix are distinct.
#

# @lc code=start

from typing import List


class Solution:
    def luckyNumbers(self, matrix: List[List[int]]) -> List[int]:
        """
        Interview explanation:
        Lucky = min of its row and max of its column. Compute row mins and
        col maxes; intersection values are lucky.

        Algorithm:
        - row_min = min each row; col_max = max each col
        - Return [x for x in row_min if x in col_max set]

        Complexity: O(mn) time, O(m+n) space.
        """
        row_min = {min(row) for row in matrix}
        col_max = {max(col) for col in zip(*matrix)}
        return list(row_min & col_max)
# @lc code=end
