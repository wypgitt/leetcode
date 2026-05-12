#
# @lc app=leetcode id=1292 lang=python3
#
# [1292] Maximum Side Length of a Square with Sum Less than or Equal to Threshold
#
# https://leetcode.com/problems/maximum-side-length-of-a-square-with-sum-less-than-or-equal-to-threshold/description/
#
# algorithms
# Medium (65.43%)
# Likes:    1547
# Dislikes: 126
# Total Accepted:    125.3K
# Total Submissions: 191.5K
# Testcase Example:  '[[1,1,3,2,4,3,2],[1,1,3,2,4,3,2],[1,1,3,2,4,3,2]]\n4'
#
# Given a m x n matrix mat and an integer threshold, return the maximum
# side-length of a square with a sum less than or equal to threshold or return
# 0 if there is no such square.
# 
# 
# Example 1:
# 
# 
# Input: mat = [[1,1,3,2,4,3,2],[1,1,3,2,4,3,2],[1,1,3,2,4,3,2]], threshold = 4
# Output: 2
# Explanation: The maximum side length of square with sum less than or equal to
# 4 is 2 as shown.
# 
# 
# Example 2:
# 
# 
# Input: mat = [[2,2,2,2,2],[2,2,2,2,2],[2,2,2,2,2],[2,2,2,2,2],[2,2,2,2,2]],
# threshold = 1
# Output: 0
# 
# 
# 
# Constraints:
# 
# 
# m == mat.length
# n == mat[i].length
# 1 <= m, n <= 300
# 0 <= mat[i][j] <= 10^4
# 0 <= threshold <= 10^5
# 
# 
#

# @lc code=start
from typing import List


class Solution:
    def maxSideLength(self, mat: List[List[int]], threshold: int) -> int:
        rows, cols = len(mat), len(mat[0])
        prefix = [[0] * (cols + 1) for _ in range(rows + 1)]

        for r in range(rows):
            row_sum = 0
            for c in range(cols):
                row_sum += mat[r][c]
                prefix[r + 1][c + 1] = prefix[r][c + 1] + row_sum

        def square_sum(row: int, col: int, size: int) -> int:
            bottom = row + size
            right = col + size
            return (
                prefix[bottom][right]
                - prefix[row][right]
                - prefix[bottom][col]
                + prefix[row][col]
            )

        def exists(size: int) -> bool:
            for r in range(rows - size + 1):
                for c in range(cols - size + 1):
                    if square_sum(r, c, size) <= threshold:
                        return True
            return False

        left, right = 0, min(rows, cols)

        while left < right:
            mid = (left + right + 1) // 2
            if exists(mid):
                left = mid
            else:
                right = mid - 1

        return left
# @lc code=end

# Explanation
# -----------
# Build a 2D prefix-sum matrix so any square sum can be queried in O(1). Then
# binary search the side length. If any square of size k has sum <= threshold,
# then smaller sizes are also possible; if none exist, larger sizes are
# impossible. That monotonic property drives the search.
#
# The prefix sum is the key data structure: without it, checking each square
# would repeatedly sum the same cells.
#
# Edge cases: answer 0 when no single cell fits; threshold large enough for the
# whole smaller dimension; rectangular matrices.
#
# Time complexity: O(mn log min(m, n)).
# Space complexity: O(mn) for the prefix matrix.
