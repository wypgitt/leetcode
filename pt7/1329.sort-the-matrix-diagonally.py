#
# @lc app=leetcode id=1329 lang=python3
#
# [1329] Sort the Matrix Diagonally
#
# https://leetcode.com/problems/sort-the-matrix-diagonally/description/
#
# algorithms
# Medium (83.18%)
# Likes:    3589
# Dislikes: 239
# Total Accepted:    198.1K
# Total Submissions: 238.1K
# Testcase Example:  '[[3,3,1,1],[2,2,1,2],[1,1,1,2]]'
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
# 
# Example 1:
# 
# 
# Input: mat = [[3,3,1,1],[2,2,1,2],[1,1,1,2]]
# Output: [[1,1,1,1],[1,2,2,2],[1,2,3,3]]
# 
# 
# Example 2:
# 
# 
# Input: mat =
# [[11,25,66,1,69,7],[23,55,17,45,15,52],[75,31,36,44,58,8],[22,27,33,25,68,4],[84,28,14,11,5,50]]
# Output:
# [[5,17,4,1,52,7],[11,11,25,45,8,69],[14,23,25,44,58,15],[22,27,31,36,50,66],[84,28,75,33,55,68]]
# 
# 
# 
# Constraints:
# 
# 
# m == mat.length
# n == mat[i].length
# 1 <= m, n <= 100
# 1 <= mat[i][j] <= 100
# 
# 
#

# @lc code=start
from __future__ import annotations

from collections import defaultdict
from typing import List


class Solution:
    def diagonalSort(self, mat: List[List[int]]) -> List[List[int]]:
        diagonals = defaultdict(list)
        rows, cols = len(mat), len(mat[0])

        for r in range(rows):
            for c in range(cols):
                diagonals[r - c].append(mat[r][c])

        for values in diagonals.values():
            values.sort(reverse=True)

        for r in range(rows):
            for c in range(cols):
                mat[r][c] = diagonals[r - c].pop()

        return mat
# @lc code=end

#
# Interview explanation
# ---------------------
# Idea:
# Cells on the same top-left to bottom-right diagonal share the same `r - c`
# value. Group by that key, sort each group, then write the sorted values back
# along the same diagonal.
#
# Data structure:
# `defaultdict(list)` maps each diagonal key to its values. Sorting in reverse
# lets us use `pop()` from the end, which is O(1), to place ascending values.
#
# Walkthrough:
# 1. Collect every cell value into `diagonals[r - c]`.
# 2. Sort each diagonal in descending order.
# 3. Traverse the matrix again and pop the smallest remaining value for that
#    diagonal.
#
# Edge cases:
# - 1 row or 1 column: every diagonal has one value, so the matrix is unchanged.
# - Duplicate values: sorting preserves valid nondecreasing order.
# - Rectangular matrices: the `r - c` key still identifies diagonals correctly.
#
# Complexity:
# - Time: O(mn log(min(m,n))) in aggregate, because each diagonal is sorted.
# - Space: O(mn) for the grouped values.
