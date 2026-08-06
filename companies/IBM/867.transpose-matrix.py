#
# @lc app=leetcode id=867 lang=python3
#
# [867] Transpose Matrix
#
# https://leetcode.com/problems/transpose-matrix/description/
#
# algorithms
# Easy (76.95%)
# Likes:    4238
# Dislikes: 463
# Total Accepted:    644K
# Total Submissions: 837K
# Testcase Example:  "[[1,2,3],[4,5,6],[7,8,9]]"
#
# Given a 2D integer array matrix, return the transpose of matrix.
#
# The transpose of a matrix is the matrix flipped over its main diagonal,
# switching the matrix's row and column indices.
#
# Example 1:
#
# Input: matrix = [[1,2,3],[4,5,6],[7,8,9]]
# Output: [[1,4,7],[2,5,8],[3,6,9]]
#
# Example 2:
#
# Input: matrix = [[1,2,3],[4,5,6]]
# Output: [[1,4],[2,5],[3,6]]
#
# Constraints:
#
# m == matrix.length
#
# n == matrix[i].length
#
# 1 <= m, n <= 1000
#
# 1 <= m * n <= 10^5
#
# -10^9 <= matrix[i][j] <= 10^9
#

# @lc code=start
from typing import List


class Solution:
    def transpose(self, matrix: List[List[int]]) -> List[List[int]]:
        """
        Interview explanation:
        Swap rows/cols: result[j][i] = matrix[i][j]. Build n x m matrix.

        Algorithm:
        - Return [[matrix[i][j] for i in range(m)] for j in range(n)].

        Complexity: O(m*n) time/space.
        """
        m, n = len(matrix), len(matrix[0])
        return [[matrix[i][j] for i in range(m)] for j in range(n)]
# @lc code=end

