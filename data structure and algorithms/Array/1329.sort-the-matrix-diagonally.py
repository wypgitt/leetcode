#
# @lc app=leetcode id=1329 lang=python3
#
# [1329] Sort the Matrix Diagonally
#
# https://leetcode.com/problems/sort-the-matrix-diagonally/description/
#
# algorithms
# Medium (83.25%)
# Likes:    3606
# Dislikes: 239
# Total Accepted:    201K
# Total Submissions: 242K
# Testcase Example:  "[[3,3,1,1],[2,2,1,2],[1,1,1,2]]"
#
# A matrix diagonal is a diagonal line of cells starting from some cell in
# either the topmost row or leftmost column and going in the bottom-right
# direction until reaching the matrix's end. For example, the matrix diagonal
# starting from mat[2][0], where mat is a 6 x 3 matrix, includes cells
# mat[2][0], mat[3][1], and mat[4][2].
#
# Given an m x n matrix mat of integers, sort each matrix diagonal in ascending
# order and return the resulting matrix.
#
# Example 1:
#
# Input: mat = [[3,3,1,1],[2,2,1,2],[1,1,1,2]]
# Output: [[1,1,1,1],[1,2,2,2],[1,2,3,3]]
#
# Example 2:
#
# Input: mat =
# [[11,25,66,1,69,7],[23,55,17,45,15,52],[75,31,36,44,58,8],[22,27,33,25,68,4],[84,28,14,11,5,50]]
# Output:
# [[5,17,4,1,52,7],[11,11,25,45,8,69],[14,23,25,44,58,15],[22,27,31,36,50,66],[84,28,75,33,55,68]]
#
# Constraints:
#
# m == mat.length
#
# n == mat[i].length
#
# 1 <= m, n <= 100
#
# 1 <= mat[i][j] <= 100
#

# @lc code=start
from collections import defaultdict
from typing import List


class Solution:
    def diagonalSort(self, mat: List[List[int]]) -> List[List[int]]:
        """
        Interview explanation:
        Diagonals share key i-j. Group values by diagonal, sort each ascending,
        write back in row-major order along that diagonal.

        Algorithm:
        - Map key=i-j to list of values; sort each; refill with pointers.

        Complexity: O(mn log(min(m,n))) time, O(mn) space.
        """
        m, n = len(mat), len(mat[0])
        diags = defaultdict(list)
        for i in range(m):
            for j in range(n):
                diags[i - j].append(mat[i][j])
        for k in diags:
            diags[k].sort()
        idx = defaultdict(int)
        for i in range(m):
            for j in range(n):
                k = i - j
                mat[i][j] = diags[k][idx[k]]
                idx[k] += 1
        return mat
# @lc code=end

