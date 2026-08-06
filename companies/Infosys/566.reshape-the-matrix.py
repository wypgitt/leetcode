#
# @lc app=leetcode id=566 lang=python3
#
# [566] Reshape the Matrix
#
# https://leetcode.com/problems/reshape-the-matrix/description/
#
# algorithms
# Easy (65.33%)
# Likes:    3727
# Dislikes: 440
# Total Accepted:    488K
# Total Submissions: 747K
# Testcase Example:  "[[1,2],[3,4]]"
#
# In MATLAB, there is a handy function called reshape which can reshape an m x
# n matrix into a new one with a different size r x c keeping its original
# data.
#
# You are given an m x n matrix mat and two integers r and c representing the
# number of rows and the number of columns of the wanted reshaped matrix.
#
# The reshaped matrix should be filled with all the elements of the original
# matrix in the same row-traversing order as they were.
#
# If the reshape operation with given parameters is possible and legal, output
# the new reshaped matrix; Otherwise, output the original matrix.
#
# Example 1:
#
# Input: mat = [[1,2],[3,4]], r = 1, c = 4
# Output: [[1,2,3,4]]
#
# Example 2:
#
# Input: mat = [[1,2],[3,4]], r = 2, c = 4
# Output: [[1,2],[3,4]]
#
# Constraints:
#
# m == mat.length
#
# n == mat[i].length
#
# 1 <= m, n <= 100
#
# -1000 <= mat[i][j] <= 1000
#
# 1 <= r, c <= 300
#


# @lc code=start
from typing import List
class Solution:
    def matrixReshape(self, mat: List[List[int]], r: int, c: int) -> List[List[int]]:
        """
        Interview explanation:
        Reshape is valid only when total element count is unchanged. Read the
        matrix in row-major order and write into an r×c grid the same way.

        Algorithm:
        - If m*n != r*c, return mat unchanged.
        - Flatten via index mapping: element k goes to [k//c][k%c].

        Complexity: O(mn) time, O(rc) space for the output.
        """
        m, n = len(mat), len(mat[0])
        if m * n != r * c:
            return mat
        ans = [[0] * c for _ in range(r)]
        for i in range(m * n):
            ans[i // c][i % c] = mat[i // n][i % n]
        return ans

    def matrixReshapeFlat(self, mat: List[List[int]], r: int, c: int) -> List[List[int]]:
        """
        Interview explanation:
        Explicit flatten-then-chunk version of the same idea; slightly clearer
        at the cost of an intermediate list.

        Algorithm:
        - Flatten mat row-major into a 1D list.
        - Slice into rows of length c.

        Complexity: O(mn) time, O(mn) extra space.
        """
        flat = [x for row in mat for x in row]
        if len(flat) != r * c:
            return mat
        return [flat[i * c:(i + 1) * c] for i in range(r)]
# @lc code=end

