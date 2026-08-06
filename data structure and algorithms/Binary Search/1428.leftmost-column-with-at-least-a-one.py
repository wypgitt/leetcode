#
# @lc app=leetcode id=1428 lang=python3
#
# [1428] Leftmost Column with at Least a One
#
# https://leetcode.com/problems/leftmost-column-with-at-least-a-one/description/
#
# algorithms
# Medium (55.27%)
# Likes:    1258
# Dislikes: 153
# Total Accepted:    199.4K
# Total Submissions: 360.7K
# Testcase Example:  "[[0,0],[1,1]]"
#
#
# A row-sorted binary matrix means that all elements are 0 or 1 and each
# row of the matrix is sorted in non-decreasing order.
#
# Given a row-sorted binary matrix binaryMatrix, return the index
# (0-indexed) of the leftmost column with a 1 in it. If such an index does
# not exist, return -1.
#
# You can't access the Binary Matrix directly. You may only access the
# matrix using a BinaryMatrix interface:
#
# BinaryMatrix.get(row, col) returns the element of the matrix at index
# (row, col) (0-indexed).
#
# BinaryMatrix.dimensions() returns the dimensions of the matrix as a list
# of 2 elements [rows, cols], which means the matrix is rows x cols.
#
# Submissions making more than 1000 calls to BinaryMatrix.get will be
# judged Wrong Answer. Also, any solutions that attempt to circumvent the
# judge will result in disqualification.
#
# For custom testing purposes, the input will be the entire binary matrix
# mat. You will not have access to the binary matrix directly.
#
# Example 1:
#
# Input: mat = [[0,0],[1,1]]
# Output: 0
#
# Example 2:
#
# Input: mat = [[0,0],[0,1]]
# Output: 1
#
# Example 3:
#
# Input: mat = [[0,0],[0,0]]
# Output: -1
#
# Constraints:
#
# rows == mat.length
#
# cols == mat[i].length
#
# 1 <= rows, cols <= 100
#
# mat[i][j] is either 0 or 1.
#
# mat[i] is sorted in non-decreasing order.
#
# @lc code=start
from typing import List

try:
    BinaryMatrix  # type: ignore[name-defined]
except NameError:

    class BinaryMatrix:  # type: ignore[no-redef]
        def get(self, row: int, col: int) -> int:
            return 0

        def dimensions(self) -> List[int]:
            return [0, 0]


class Solution:
    def leftMostColumnWithOne(self, binaryMatrix: "BinaryMatrix") -> int:
        """
        Interview explanation:
        Premium. Row-sorted binary matrix via BinaryMatrix API (get/dimensions).
        Find leftmost column containing a 1, or -1. Start top-right; move left
        on 1, down on 0 (staircase) — minimizes get calls.

        Algorithm:
        (staircase)
        - rows, cols = dimensions(); r=0,c=cols-1; ans=-1
        - while r<rows and c>=0: if get(r,c)==1: ans=c; c-=1 else r+=1

        Complexity: O(rows+cols) get calls, O(1) space.
        """
        rows, cols = binaryMatrix.dimensions()
        r, c = 0, cols - 1
        ans = -1
        while r < rows and c >= 0:
            if binaryMatrix.get(r, c) == 1:
                ans = c
                c -= 1
            else:
                r += 1
        return ans

    def leftMostColumnWithOne_binary(self, binaryMatrix: "BinaryMatrix") -> int:
        """
        Interview explanation:
        Alternate: binary search each row for first 1; track global min column.

        Algorithm:
        - For each row lo/hi binary search first 1; update answer.

        Complexity: O(rows * log cols) gets, O(1) space.
        """
        rows, cols = binaryMatrix.dimensions()
        ans = cols
        for r in range(rows):
            lo, hi = 0, cols - 1
            first = cols
            while lo <= hi:
                mid = (lo + hi) // 2
                if binaryMatrix.get(r, mid) == 1:
                    first = mid
                    hi = mid - 1
                else:
                    lo = mid + 1
            ans = min(ans, first)
        return ans if ans < cols else -1
# @lc code=end
