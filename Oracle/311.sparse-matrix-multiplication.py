#
# @lc app=leetcode id=311 lang=python3
#
# [311] Sparse Matrix Multiplication
#
# https://leetcode.com/problems/sparse-matrix-multiplication/description/
#
# algorithms
# Medium (69.33%)
# Likes:    1131
# Dislikes: 374
# Total Accepted:    224.9K
# Total Submissions: 324.3K
# Testcase Example:  "[[1,0,0],[-1,0,3]]\n[[7,0,0],[0,0,0],[0,0,1]]"
#
#
# Given two sparse matrices mat1 of size m x k and mat2 of size k x n,
# return the result of mat1 x mat2. You may assume that multiplication is
# always possible.
#
# Example 1:
#
# Input: mat1 = [[1,0,0],[-1,0,3]], mat2 = [[7,0,0],[0,0,0],[0,0,1]]
# Output: [[7,0,0],[-7,0,3]]
#
# Example 2:
#
# Input: mat1 = [[0]], mat2 = [[0]]
# Output: [[0]]
#
# Constraints:
#
# m == mat1.length
#
# k == mat1[i].length == mat2.length
#
# n == mat2[i].length
#
# 1 <= m, n, k <= 100
#
# -100 <= mat1[i][j], mat2[i][j] <= 100
#
# @lc code=start
from typing import List


class Solution:
    def multiply(self, mat1: List[List[int]], mat2: List[List[int]]) -> List[List[int]]:
        """
        Interview explanation:
        Sparse multiply: only iterate non-zero entries of mat1 and corresponding
        rows of mat2 to accumulate into the result.

        Algorithm:
        - For each mat1[i][k] != 0, for each mat2[k][j] != 0:
          result[i][j] += mat1[i][k] * mat2[k][j].

        Complexity: O(n_nonzero) better than O(m*n*p) when sparse; O(mp) space.
        """
        m, k = len(mat1), len(mat1[0])
        n = len(mat2[0])
        res = [[0] * n for _ in range(m)]
        for i in range(m):
            for t in range(k):
                if mat1[i][t] == 0:
                    continue
                for j in range(n):
                    if mat2[t][j] != 0:
                        res[i][j] += mat1[i][t] * mat2[t][j]
        return res
# @lc code=end

