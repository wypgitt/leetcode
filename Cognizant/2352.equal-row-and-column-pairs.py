#
# @lc app=leetcode id=2352 lang=python3
#
# [2352] Equal Row and Column Pairs
#
# https://leetcode.com/problems/equal-row-and-column-pairs/description/
#
# algorithms
# Medium (71.20%)
# Likes:    2519
# Dislikes: 192
# Total Accepted:    424.9K
# Total Submissions: 596.7K
# Testcase Example:  "[[3,2,1],[1,7,6],[2,7,7]]"
#
# Given a 0-indexed n x n integer matrix grid, return the number of pairs (r_i,
# c_j) such that row r_i and column c_j are equal.
#
# A row and column pair is considered equal if they contain the same elements in
# the same order (i.e., an equal array).
#
#
#
# Example 1:
#
# Input: grid = [[3,2,1],[1,7,6],[2,7,7]]
# Output: 1
# Explanation: There is 1 equal row and column pair:
# - (Row 2, Column 1): [2,7,7]
#
# Example 2:
#
# Input: grid = [[3,1,2,2],[1,4,4,5],[2,4,2,2],[2,4,2,2]]
# Output: 3
# Explanation: There are 3 equal row and column pairs:
# - (Row 0, Column 0): [3,1,2,2]
# - (Row 2, Column 2): [2,4,2,2]
# - (Row 3, Column 2): [2,4,2,2]
#
#
#
# Constraints:
#
#
# n == grid.length == grid[i].length
#
#
# 1 <= n <= 200
#
#
# 1 <= grid[i][j] <= 10^5
#

# @lc code=start

from typing import List
from collections import Counter


class Solution:
    def equalPairs(self, grid: List[List[int]]) -> int:
        """
        Interview explanation:
        Count pairs (r, c) where row r equals column c as sequences.

        Algorithm:
        - Hash-count rows (as tuples); for each column, add row-count of that tuple.

        Complexity: O(n^2) time, O(n^2) space.
        """
        n = len(grid)
        row_cnt = Counter(tuple(row) for row in grid)
        ans = 0
        for c in range(n):
            col = tuple(grid[r][c] for r in range(n))
            ans += row_cnt[col]
        return ans

    def equalPairs_transpose(self, grid: List[List[int]]) -> int:
        """
        Interview explanation:
        Alternate: build transposed grid and count matching row/column tuples.

        Algorithm:
        - cols = zip(*grid); Counter(rows) vs Counter(cols) multiply frequencies.

        Complexity: O(n^2) time, O(n^2) space.
        """
        row_cnt = Counter(map(tuple, grid))
        col_cnt = Counter(zip(*grid))
        return sum(row_cnt[t] * col_cnt[t] for t in row_cnt)
# @lc code=end
