#
# @lc app=leetcode id=2536 lang=python3
#
# [2536] Increment Submatrices by One
#
# https://leetcode.com/problems/increment-submatrices-by-one/description/
#
# algorithms
# Medium (73.85%)
# Likes:    896
# Dislikes: 81
# Total Accepted:    110.3K
# Total Submissions: 149.3K
# Testcase Example:  "3\n[[1,1,2,2],[0,0,1,1]]"
#
# You are given a positive integer n, indicating that we initially have an n x
# n 0-indexed integer matrix mat filled with zeroes.
#
# You are also given a 2D integer array query. For each query[i] = [row1_i,
# col1_i, row2_i, col2_i], you should do the following operation:
#
#
# Add 1 to every element in the submatrix with the top left corner (row1_i,
# col1_i) and the bottom right corner (row2_i, col2_i). That is, add 1 to
# mat[x][y] for all row1_i <= x <= row2_i and col1_i <= y <= col2_i.
#
# Return the matrix mat after performing every query.
#
#
#
# Example 1:
#
# Input: n = 3, queries = [[1,1,2,2],[0,0,1,1]]
# Output: [[1,1,0],[1,2,1],[0,1,1]]
# Explanation: The diagram above shows the initial matrix, the matrix after the
# first query, and the matrix after the second query.
# - In the first query, we add 1 to every element in the submatrix with the top
# left corner (1, 1) and bottom right corner (2, 2).
# - In the second query, we add 1 to every element in the submatrix with the top
# left corner (0, 0) and bottom right corner (1, 1).
#
# Example 2:
#
# Input: n = 2, queries = [[0,0,1,1]]
# Output: [[1,1],[1,1]]
# Explanation: The diagram above shows the initial matrix and the matrix after
# the first query.
# - In the first query we add 1 to every element in the matrix.
#
#
#
# Constraints:
#
#
# 1 <= n <= 500
#
#
# 1 <= queries.length <= 10^4
#
#
# 0 <= row1_i <= row2_i < n
#
#
# 0 <= col1_i <= col2_i < n
#

# @lc code=start
from typing import List


class Solution:
    def rangeAddQueries(self, n: int, queries: List[List[int]]) -> List[List[int]]:
        """
        Interview explanation:
        Start from n x n zeros; for each query add 1 to a rectangular submatrix;
        return the final matrix.

        Algorithm:
        (2D difference array)
        - For [r1,c1,r2,c2]: diff[r1][c1]+=1, diff[r1][c2+1]-=1,
          diff[r2+1][c1]-=1, diff[r2+1][c2+1]+=1.
        - Prefix-sum rows then columns (or 2D inclusive scan) to materialize.

        Complexity: O(n^2 + q) time, O(n^2) space.
        """
        diff = [[0] * (n + 1) for _ in range(n + 1)]
        for r1, c1, r2, c2 in queries:
            diff[r1][c1] += 1
            diff[r1][c2 + 1] -= 1
            diff[r2 + 1][c1] -= 1
            diff[r2 + 1][c2 + 1] += 1

        mat = [[0] * n for _ in range(n)]
        for i in range(n):
            for j in range(n):
                v = diff[i][j]
                if i:
                    v += mat[i - 1][j]
                if j:
                    v += mat[i][j - 1]
                if i and j:
                    v -= mat[i - 1][j - 1]
                mat[i][j] = v
        return mat
# @lc code=end
