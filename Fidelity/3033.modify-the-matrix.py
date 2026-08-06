#
# @lc app=leetcode id=3033 lang=python3
#
# [3033] Modify the Matrix
#
# https://leetcode.com/problems/modify-the-matrix/description/
#
# algorithms
# Easy (68.95%)
# Likes:    157
# Dislikes: 9
# Total Accepted:    60.8K
# Total Submissions: 88.2K
# Testcase Example:  "[[1,2,-1],[4,-1,6],[7,8,9]]"
#
#
# Given a 0-indexed m x n integer matrix matrix, create a new 0-indexed
# matrix called answer. Make answer equal to matrix, then replace each
# element with the value -1 with the maximum element in its respective
# column.
#
# Return the matrix answer.
#
# Example 1:
#
# Input: matrix = [[1,2,-1],[4,-1,6],[7,8,9]]
# Output: [[1,2,9],[4,8,6],[7,8,9]]
# Explanation: The diagram above shows the elements that are changed (in
# blue).
# - We replace the value in the cell [1][1] with the maximum value in the
# column 1, that is 8.
# - We replace the value in the cell [0][2] with the maximum value in the
# column 2, that is 9.
#
# Example 2:
#
# Input: matrix = [[3,-1],[5,2]]
# Output: [[3,2],[5,2]]
# Explanation: The diagram above shows the elements that are changed (in
# blue).
#
# Constraints:
#
# m == matrix.length
#
# n == matrix[i].length
#
# 2 <= m, n <= 50
#
# -1 <= matrix[i][j] <= 100
#
# The input is generated such that each column contains at least one
# non-negative integer.
#

# @lc code=start

from typing import List


class Solution:
    def modifiedMatrix(self, matrix: List[List[int]]) -> List[List[int]]:
        """
        Interview explanation:
        Replace every -1 with the max value in its column.

        Algorithm:
        - Precompute column maxima; copy matrix replacing -1 cells.

        Complexity: O(m*n) time, O(n) extra space (or O(m*n) for the answer).
        """
        m, n = len(matrix), len(matrix[0])
        col_max = [max(matrix[i][j] for i in range(m)) for j in range(n)]
        return [
            [col_max[j] if matrix[i][j] == -1 else matrix[i][j] for j in range(n)]
            for i in range(m)
        ]
# @lc code=end
