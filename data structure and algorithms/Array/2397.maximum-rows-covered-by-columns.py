#
# @lc app=leetcode id=2397 lang=python3
#
# [2397] Maximum Rows Covered by Columns
#
# https://leetcode.com/problems/maximum-rows-covered-by-columns/description/
#
# algorithms
# Medium (58.21%)
# Likes:    301
# Dislikes: 447
# Total Accepted:    20.8K
# Total Submissions: 35.7K
# Testcase Example:  "[[0,0,0],[1,0,1],[0,1,1],[0,0,1]]\n2"
#
# You are given an m x n binary matrix matrix and an integer numSelect.
#
# Your goal is to select exactly numSelect distinct columns from matrix such
# that you cover as many rows as possible.
#
# A row is considered covered if all the 1's in that row are also part of a
# column that you have selected. If a row does not have any 1s, it is also
# considered covered.
#
# More formally, let us consider selected = {c_1, c_2, ...., c_numSelect} as the
# set of columns selected by you. A row i is covered by selected if:
#
#
# For each cell where matrix[i][j] == 1, the column j is in selected.
#
#
# Or, no cell in row i has a value of 1.
#
# Return the maximum number of rows that can be covered by a set of numSelect
# columns.
#
#
#
# Example 1:
#
# Input: matrix = [[0,0,0],[1,0,1],[0,1,1],[0,0,1]], numSelect = 2
#
# Output: 3
#
# Explanation:
#
# One possible way to cover 3 rows is shown in the diagram above.
#
# We choose s = {0, 2}.
#
# - Row 0 is covered because it has no occurrences of 1.
#
# - Row 1 is covered because the columns with value 1, i.e. 0 and 2 are present
# in s.
#
# - Row 2 is not covered because matrix[2][1] == 1 but 1 is not present in s.
#
# - Row 3 is covered because matrix[2][2] == 1 and 2 is present in s.
#
# Thus, we can cover three rows.
#
# Note that s = {1, 2} will also cover 3 rows, but it can be shown that no more
# than three rows can be covered.
#
# Example 2:
#
# Input: matrix = [[1],[0]], numSelect = 1
#
# Output: 2
#
# Explanation:
#
# Selecting the only column will result in both rows being covered since the
# entire matrix is selected.
#
#
#
# Constraints:
#
#
# m == matrix.length
#
#
# n == matrix[i].length
#
#
# 1 <= m, n <= 12
#
#
# matrix[i][j] is either 0 or 1.
#
#
# 1 <= numSelect <= n
#

# @lc code=start

from typing import List
from itertools import combinations


class Solution:
    def maximumRows(self, matrix: List[List[int]], numSelect: int) -> int:
        """
        Interview explanation:
        Choose numSelect columns; a row is covered if all its 1s lie in chosen
        columns. Maximize covered rows.

        Algorithm:
        - Bitmask rows; enumerate all column subsets of size numSelect; count
          rows whose 1-bits ⊆ chosen mask.

        Complexity: O(C(n,numSelect) * m) time, O(m) space. n,m <= 12.
        """
        m, n = len(matrix), len(matrix[0])
        rows = []
        for r in matrix:
            mask = 0
            for j, v in enumerate(r):
                if v:
                    mask |= 1 << j
            rows.append(mask)
        ans = 0
        for cols in combinations(range(n), numSelect):
            chosen = 0
            for c in cols:
                chosen |= 1 << c
            covered = sum(1 for rm in rows if rm & ~chosen == 0)
            ans = max(ans, covered)
        return ans

    def maximumRows_bit(self, matrix: List[List[int]], numSelect: int) -> int:
        """
        Interview explanation:
        Alternate: iterate all bitmasks with popcount == numSelect.

        Algorithm:
        - For mask in 0..2^n-1 with k bits; count covered rows.

        Complexity: O(2^n * m) time, O(m) space.
        """
        m, n = len(matrix), len(matrix[0])
        rows = [0] * m
        for i, r in enumerate(matrix):
            for j, v in enumerate(r):
                if v:
                    rows[i] |= 1 << j
        ans = 0
        for mask in range(1 << n):
            if mask.bit_count() != numSelect:
                continue
            ans = max(ans, sum(1 for rm in rows if rm & ~mask == 0))
        return ans
# @lc code=end
