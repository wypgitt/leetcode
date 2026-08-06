#
# @lc app=leetcode id=1314 lang=python3
#
# [1314] Matrix Block Sum
#
# https://leetcode.com/problems/matrix-block-sum/description/
#
# algorithms
# Medium (76.81%)
# Likes:    2542
# Dislikes: 403
# Total Accepted:    117K
# Total Submissions: 153K
# Testcase Example:  "[[1,2,3],[4,5,6],[7,8,9]]"
#
# Given a m x n matrix mat and an integer k, return a matrix answer where each
# answer[i][j] is the sum of all elements mat[r][c] for:
#
# i - k <= r <= i + k,
#
# j - k <= c <= j + k, and
#
# (r, c) is a valid position in the matrix.
#
# Example 1:
#
# Input: mat = [[1,2,3],[4,5,6],[7,8,9]], k = 1
# Output: [[12,21,16],[27,45,33],[24,39,28]]
#
# Example 2:
#
# Input: mat = [[1,2,3],[4,5,6],[7,8,9]], k = 2
# Output: [[45,45,45],[45,45,45],[45,45,45]]
#
# Constraints:
#
# m == mat.length
#
# n == mat[i].length
#
# 1 <= m, n, k <= 100
#
# 1 <= mat[i][j] <= 100
#

# @lc code=start
from typing import List


class Solution:
    def matrixBlockSum(self, mat: List[List[int]], k: int) -> List[List[int]]:
        """
        Interview explanation:
        answer[i][j] = sum of mat[r][c] for |r-i|<=k and |c-j|<=k. 2D prefix
        sums answer each rectangle in O(1).

        Algorithm:
        - pref[i+1][j+1] = sum of mat[:i][:j]
        - For each cell clamp rectangle and query prefix.

        Complexity: O(mn) time/space.
        """
        m, n = len(mat), len(mat[0])
        pref = [[0] * (n + 1) for _ in range(m + 1)]
        for i in range(m):
            for j in range(n):
                pref[i + 1][j + 1] = (
                    mat[i][j] + pref[i][j + 1] + pref[i + 1][j] - pref[i][j]
                )

        def rect(r1, c1, r2, c2):
            return (
                pref[r2 + 1][c2 + 1]
                - pref[r1][c2 + 1]
                - pref[r2 + 1][c1]
                + pref[r1][c1]
            )

        ans = [[0] * n for _ in range(m)]
        for i in range(m):
            for j in range(n):
                r1, c1 = max(0, i - k), max(0, j - k)
                r2, c2 = min(m - 1, i + k), min(n - 1, j + k)
                ans[i][j] = rect(r1, c1, r2, c2)
        return ans
# @lc code=end

