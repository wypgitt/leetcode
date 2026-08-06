#
# @lc app=leetcode id=2661 lang=python3
#
# [2661] First Completely Painted Row or Column
#
# https://leetcode.com/problems/first-completely-painted-row-or-column/description/
#
# algorithms
# Medium (63.86%)
# Likes:    1117
# Dislikes: 33
# Total Accepted:    161.3K
# Total Submissions: 252.6K
# Testcase Example:  "[1,3,4,2]\n[[1,4],[2,3]]"
#
# You are given a 0-indexed integer array arr, and an m x n integer matrix mat.
# arr and mat both contain all the integers in the range [1, m * n].
#
# Go through each index i in arr starting from index 0 and paint the cell in mat
# containing the integer arr[i].
#
# Return the smallest index i at which either a row or a column will be
# completely painted in mat.
#
#
#
# Example 1:
#
# Input: arr = [1,3,4,2], mat = [[1,4],[2,3]]
# Output: 2
# Explanation: The moves are shown in order, and both the first row and second
# column of the matrix become fully painted at arr[2].
#
# Example 2:
#
# Input: arr = [2,8,7,4,1,3,5,6,9], mat = [[3,2,5],[1,4,6],[8,7,9]]
# Output: 3
# Explanation: The second column becomes fully painted at arr[3].
#
#
#
# Constraints:
#
#
# m == mat.length
#
#
# n = mat[i].length
#
#
# arr.length == m * n
#
#
# 1 <= m, n <= 10^5
#
#
# 1 <= m * n <= 10^5
#
#
# 1 <= arr[i], mat[r][c] <= m * n
#
#
# All the integers of arr are unique.
#
#
# All the integers of mat are unique.
#

# @lc code=start

from typing import List


class Solution:
    def firstCompleteIndex(self, arr: List[int], mat: List[List[int]]) -> int:
        """
        Interview explanation:
        Paint mat cells in arr order; return first index when some row or column is fully painted.

        Algorithm:
        - Map value -> (r,c); track painted counts per row/col; return when count hits n or m.

        Complexity: O(mn) time, O(mn) space.
        """
        m, n = len(mat), len(mat[0])
        pos = {}
        for i in range(m):
            for j in range(n):
                pos[mat[i][j]] = (i, j)
        row = [0] * m
        col = [0] * n
        for i, v in enumerate(arr):
            r, c = pos[v]
            row[r] += 1
            col[c] += 1
            if row[r] == n or col[c] == m:
                return i
        return -1
# @lc code=end
