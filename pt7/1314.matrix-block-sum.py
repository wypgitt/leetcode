#
# @lc app=leetcode id=1314 lang=python3
#
# [1314] Matrix Block Sum
#
# https://leetcode.com/problems/matrix-block-sum/description/
#
# algorithms
# Medium (76.50%)
# Likes:    2516
# Dislikes: 402
# Total Accepted:    112.1K
# Total Submissions: 146.5K
# Testcase Example:  '[[1,2,3],[4,5,6],[7,8,9]]\n1'
#
# Given a m x n matrix mat and an integer k, return a matrix answer where each
# answer[i][j] is the sum of all elements mat[r][c] for:
# 
# 
# i - k <= r <= i + k,
# j - k <= c <= j + k, and
# (r, c) is a valid position in the matrix.
# 
# 
# 
# Example 1:
# 
# 
# Input: mat = [[1,2,3],[4,5,6],[7,8,9]], k = 1
# Output: [[12,21,16],[27,45,33],[24,39,28]]
# 
# 
# Example 2:
# 
# 
# Input: mat = [[1,2,3],[4,5,6],[7,8,9]], k = 2
# Output: [[45,45,45],[45,45,45],[45,45,45]]
# 
# 
# 
# Constraints:
# 
# 
# m == mat.length
# n == mat[i].length
# 1 <= m, n, k <= 100
# 1 <= mat[i][j] <= 100
# 
# 
#

# @lc code=start
from __future__ import annotations

from typing import List


class Solution:
    def matrixBlockSum(self, mat: List[List[int]], k: int) -> List[List[int]]:
        rows, cols = len(mat), len(mat[0])
        prefix = [[0] * (cols + 1) for _ in range(rows + 1)]

        for r in range(rows):
            for c in range(cols):
                prefix[r + 1][c + 1] = (
                    mat[r][c]
                    + prefix[r][c + 1]
                    + prefix[r + 1][c]
                    - prefix[r][c]
                )

        answer = [[0] * cols for _ in range(rows)]

        for r in range(rows):
            top = max(0, r - k)
            bottom = min(rows - 1, r + k)
            for c in range(cols):
                left = max(0, c - k)
                right = min(cols - 1, c + k)
                answer[r][c] = (
                    prefix[bottom + 1][right + 1]
                    - prefix[top][right + 1]
                    - prefix[bottom + 1][left]
                    + prefix[top][left]
                )

        return answer
# @lc code=end

#
# Interview explanation
# ---------------------
# Idea:
# Each answer cell asks for a rectangular sum centered at `(r, c)`. Computing
# that rectangle by scanning every cell would be too slow. A 2D prefix sum
# lets us answer any rectangle sum in O(1).
#
# Data structure:
# `prefix` has one extra row and column of zeros. This padding removes boundary
# special cases from the rectangle formula.
#
# Rectangle formula:
# Sum of rows `[top..bottom]` and columns `[left..right]` is:
# prefix[bottom+1][right+1]
# - prefix[top][right+1]
# - prefix[bottom+1][left]
# + prefix[top][left]
#
# Edge cases:
# - `k = 0`: each block is the cell itself.
# - `k` larger than the matrix: bounds clamp to the whole matrix.
# - Single row or column: the same rectangle formula still works.
#
# Complexity:
# - Time: O(mn), one pass to build the prefix table and one pass for answers.
# - Space: O(mn), for the prefix table and output.
