#
# @lc app=leetcode id=1252 lang=python3
#
# [1252] Cells with Odd Values in a Matrix
#
# https://leetcode.com/problems/cells-with-odd-values-in-a-matrix/description/
#
# algorithms
# Easy (79.89%)
# Likes:    1356
# Dislikes: 1563
# Total Accepted:    148K
# Total Submissions: 185K
# Testcase Example:  "2"
#
# There is an m x n matrix that is initialized to all 0's. There is also a 2D
# array indices where each indices[i] = [r_i, c_i] represents a 0-indexed
# location to perform some increment operations on the matrix.
#
# For each location indices[i], do both of the following:
#
# Increment all the cells on row r_i.
#
# Increment all the cells on column c_i.
#
# Given m, n, and indices, return the number of odd-valued cells in the matrix
# after applying the increment to all locations in indices.
#
# Example 1:
#
# Input: m = 2, n = 3, indices = [[0,1],[1,1]]
# Output: 6
# Explanation: Initial matrix = [[0,0,0],[0,0,0]].
# After applying first increment it becomes [[1,2,1],[0,1,0]].
# The final matrix is [[1,3,1],[1,3,1]], which contains 6 odd numbers.
#
# Example 2:
#
# Input: m = 2, n = 2, indices = [[1,1],[0,0]]
# Output: 0
# Explanation: Final matrix = [[2,2],[2,2]]. There are no odd numbers in the
# final matrix.
#
# Constraints:
#
# 1 <= m, n <= 50
#
# 1 <= indices.length <= 100
#
# 0 <= r_i < m
#
# 0 <= c_i < n
#
# Follow up: Could you solve this in O(n + m + indices.length) time with only
# O(n + m) extra space?
#

# @lc code=start

from typing import List


class Solution:
    def oddCells(self, m: int, n: int, indices: List[List[int]]) -> int:
        """
        Interview explanation:
        Incrementing a cell's row and column flips parity. Final cell (i,j) is
        odd iff row[i]+col[j] is odd. Count row/col increment counts, then
        count odd combinations: odd_rows*even_cols + even_rows*odd_cols.

        Algorithm:
        - rows[m]=0, cols[n]=0; for r,c in indices: rows[r]+=1; cols[c]+=1.
        - odd_r = count odd rows; odd_c similarly.
        - return odd_r*(n-odd_c) + (m-odd_r)*odd_c.

        Complexity: O(m+n+|indices|) time, O(m+n) space.
        """
        rows = [0] * m
        cols = [0] * n
        for r, c in indices:
            rows[r] += 1
            cols[c] += 1
        odd_r = sum(x & 1 for x in rows)
        odd_c = sum(x & 1 for x in cols)
        return odd_r * (n - odd_c) + (m - odd_r) * odd_c

    def oddCells_simulate(self, m: int, n: int, indices: List[List[int]]) -> int:
        """
        Interview explanation:
        Alternate direct simulation with a matrix (fine for small m,n).

        Algorithm:
        - Zero matrix; apply each index increment; count odd cells.

        Complexity: O(m*n + |indices|*(m+n)) time, O(m*n) space.
        """
        mat = [[0] * n for _ in range(m)]
        for r, c in indices:
            for j in range(n):
                mat[r][j] += 1
            for i in range(m):
                mat[i][c] += 1
        return sum(v & 1 for row in mat for v in row)
# @lc code=end
