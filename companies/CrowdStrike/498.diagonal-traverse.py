#
# @lc app=leetcode id=498 lang=python3
#
# [498] Diagonal Traverse
#
# https://leetcode.com/problems/diagonal-traverse/description/
#
# algorithms
# Medium (67.34%)
# Likes:    4358
# Dislikes: 787
# Total Accepted:    572K
# Total Submissions: 849K
# Testcase Example:  "[[1,2,3],[4,5,6],[7,8,9]]"
#
# Given an m x n matrix mat, return an array of all the elements of the array
# in a diagonal order.
#
# Example 1:
#
# Input: mat = [[1,2,3],[4,5,6],[7,8,9]]
# Output: [1,2,4,7,5,3,6,8,9]
#
# Example 2:
#
# Input: mat = [[1,2],[3,4]]
# Output: [1,2,3,4]
#
# Constraints:
#
# m == mat.length
#
# n == mat[i].length
#
# 1 <= m, n <= 10^4
#
# 1 <= m * n <= 10^4
#
# -10^5 <= mat[i][j] <= 10^5
#

# @lc code=start
from typing import List


class Solution:
    def findDiagonalOrder(self, mat: List[List[int]]) -> List[int]:
        """
        Interview explanation:
        Traverse diagonals where r+c is constant; even diagonals go up-right,
        odd go down-left. Simulate with direction flips at boundaries.

        Algorithm:
        - r=c=0; dir = up-right (-1,+1); for each of m*n cells: append;
          if hitting border with current dir, move to next diagonal start and
          flip direction.

        Complexity: O(mn) time, O(1) extra space (besides output).
        """
        if not mat or not mat[0]:
            return []
        m, n = len(mat), len(mat[0])
        ans = []
        r = c = 0
        up = True
        for _ in range(m * n):
            ans.append(mat[r][c])
            if up:
                if c == n - 1:
                    r += 1
                    up = False
                elif r == 0:
                    c += 1
                    up = False
                else:
                    r -= 1
                    c += 1
            else:
                if r == m - 1:
                    c += 1
                    up = True
                elif c == 0:
                    r += 1
                    up = True
                else:
                    r += 1
                    c -= 1
        return ans
# @lc code=end
