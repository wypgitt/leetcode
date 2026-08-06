#
# @lc app=leetcode id=1901 lang=python3
#
# [1901] Find a Peak Element II
#
# https://leetcode.com/problems/find-a-peak-element-ii/description/
#
# algorithms
# Medium (55.46%)
# Likes:    2791
# Dislikes: 165
# Total Accepted:    206K
# Total Submissions: 371K
# Testcase Example:  "[[1,4],[3,2]]"
#
# A peak element in a 2D grid is an element that is strictly greater than all
# of its adjacent neighbors to the left, right, top, and bottom.
#
# Given a 0-indexed m x n matrix mat where no two adjacent cells are equal,
# find any peak element mat[i][j] and return the length 2 array [i,j].
#
# You may assume that the entire matrix is surrounded by an outer perimeter
# with the value -1 in each cell.
#
# You must write an algorithm that runs in O(m log(n)) or O(n log(m)) time.
#
# Example 1:
#
# Input: mat = [[1,4],[3,2]]
# Output: [0,1]
# Explanation: Both 3 and 4 are peak elements so [1,0] and [0,1] are both
# acceptable answers.
#
# Example 2:
#
# Input: mat = [[10,20,15],[21,30,14],[7,16,32]]
# Output: [1,1]
# Explanation: Both 30 and 32 are peak elements so [1,1] and [2,2] are both
# acceptable answers.
#
# Constraints:
#
# m == mat.length
#
# n == mat[i].length
#
# 1 <= m, n <= 500
#
# 1 <= mat[i][j] <= 10^5
#
# No two adjacent cells are equal.
#

# @lc code=start
from typing import List


class Solution:
    def findPeakGrid(self, mat: List[List[int]]) -> List[int]:
        """
        Interview explanation:
        2D peak (strictly greater than 4-neighbors). Binary search on columns:
        pick mid column's max cell; if a neighbor column is taller, search that half.

        Algorithm:
        - lo,hi = 0,n-1. Mid column; find max row i. Compare mat[i][mid] to left/right.
          Move search to taller neighbor side; else (i,mid) is a peak.

        Complexity: O(m log n) time, O(1) space.
        """
        m, n = len(mat), len(mat[0])
        lo, hi = 0, n - 1
        while lo <= hi:
            mid = (lo + hi) // 2
            i = max(range(m), key=lambda r: mat[r][mid])
            left = mat[i][mid - 1] if mid > 0 else -1
            right = mat[i][mid + 1] if mid + 1 < n else -1
            if mat[i][mid] >= left and mat[i][mid] >= right:
                return [i, mid]
            if left > mat[i][mid]:
                hi = mid - 1
            else:
                lo = mid + 1
        return [0, 0]

    def findPeakGrid_rows(self, mat: List[List[int]]) -> List[int]:
        """
        Interview explanation:
        Classic alternate: binary search on rows instead of columns (O(n log m)).

        Algorithm:
        - Mid row's max column; compare up/down neighbors; discard half.

        Complexity: O(n log m) time, O(1) space.
        """
        m, n = len(mat), len(mat[0])
        lo, hi = 0, m - 1
        while lo <= hi:
            mid = (lo + hi) // 2
            j = max(range(n), key=lambda c: mat[mid][c])
            up = mat[mid - 1][j] if mid > 0 else -1
            down = mat[mid + 1][j] if mid + 1 < m else -1
            if mat[mid][j] >= up and mat[mid][j] >= down:
                return [mid, j]
            if up > mat[mid][j]:
                hi = mid - 1
            else:
                lo = mid + 1
        return [0, 0]
# @lc code=end
