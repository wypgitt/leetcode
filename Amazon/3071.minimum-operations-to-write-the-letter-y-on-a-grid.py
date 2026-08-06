#
# @lc app=leetcode id=3071 lang=python3
#
# [3071] Minimum Operations to Write the Letter Y on a Grid
#
# https://leetcode.com/problems/minimum-operations-to-write-the-letter-y-on-a-grid/description/
#
# algorithms
# Medium (64.75%)
# Likes:    151
# Dislikes: 34
# Total Accepted:    37.8K
# Total Submissions: 58.3K
# Testcase Example:  "[[1,2,2],[1,1,0],[0,1,0]]"
#
#
# You are given a 0-indexed n x n grid where n is odd, and grid[r][c] is
# 0, 1, or 2.
#
# We say that a cell belongs to the Letter Y if it belongs to one of the
# following:
#
# The diagonal starting at the top-left cell and ending at the center cell
# of the grid.
#
# The diagonal starting at the top-right cell and ending at the center
# cell of the grid.
#
# The vertical line starting at the center cell and ending at the bottom
# border of the grid.
#
# The Letter Y is written on the grid if and only if:
#
# All values at cells belonging to the Y are equal.
#
# All values at cells not belonging to the Y are equal.
#
# The values at cells belonging to the Y are different from the values at
# cells not belonging to the Y.
#
# Return the minimum number of operations needed to write the letter Y on
# the grid given that in one operation you can change the value at any
# cell to 0, 1, or 2.
#
# Example 1:
#
# Input: grid = [[1,2,2],[1,1,0],[0,1,0]]
# Output: 3
# Explanation: We can write Y on the grid by applying the changes
# highlighted in blue in the image above. After the operations, all cells
# that belong to Y, denoted in bold, have the same value of 1 while those
# that do not belong to Y are equal to 0.
# It can be shown that 3 is the minimum number of operations needed to
# write Y on the grid.
#
# Example 2:
#
# Input: grid =
# [[0,1,0,1,0],[2,1,0,1,2],[2,2,2,0,1],[2,2,2,2,2],[2,1,2,2,2]]
# Output: 12
# Explanation: We can write Y on the grid by applying the changes
# highlighted in blue in the image above. After the operations, all cells
# that belong to Y, denoted in bold, have the same value of 0 while those
# that do not belong to Y are equal to 2.
# It can be shown that 12 is the minimum number of operations needed to
# write Y on the grid.
#
# Constraints:
#
# 3 <= n <= 49
#
# n == grid.length == grid[i].length
#
# 0 <= grid[i][j] <= 2
#
# n is odd.
#

# @lc code=start
from typing import List


class Solution:
    def minimumOperationsToWriteY(self, grid: List[List[int]]) -> int:
        """
        Interview explanation:
        Y-cells (two top diagonals into center + vertical stem) must share one
        value a; non-Y cells share a different value b in {0,1,2}. Minimize
        changes.

        Algorithm:
        - Count frequencies on Y vs non-Y. Try all a != b; cost =
          (|Y| - y_cnt[a]) + (|nonY| - non_cnt[b]).

        Complexity: O(n^2) time, O(1) space.
        """
        n = len(grid)
        mid = n // 2
        y_cnt = [0, 0, 0]
        other_cnt = [0, 0, 0]
        y_cells = 0
        for i in range(n):
            for j in range(n):
                on_y = (
                    (i <= mid and i == j)
                    or (i <= mid and i + j == n - 1)
                    or (i >= mid and j == mid)
                )
                if on_y:
                    y_cnt[grid[i][j]] += 1
                    y_cells += 1
                else:
                    other_cnt[grid[i][j]] += 1
        other_cells = n * n - y_cells
        ans = n * n
        for a in range(3):
            for b in range(3):
                if a == b:
                    continue
                ans = min(ans, (y_cells - y_cnt[a]) + (other_cells - other_cnt[b]))
        return ans
# @lc code=end
