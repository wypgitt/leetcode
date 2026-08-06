#
# @lc app=leetcode id=3643 lang=python3
#
# [3643] Flip Square Submatrix Vertically
#
# https://leetcode.com/problems/flip-square-submatrix-vertically/description/
#
# algorithms
# Easy (79.39%)
# Likes:    287
# Dislikes: 29
# Total Accepted:    158.3K
# Total Submissions: 199.4K
# Testcase Example:  "[[1,2,3,4],[5,6,7,8],[9,10,11,12],[13,14,15,16]]\n1\n0\n3"
#
#
# You are given an m x n integer matrix grid, and three integers x, y, and
# k.
#
# The integers x and y represent the row and column indices of the
# top-left corner of a square submatrix and the integer k represents the
# size (side length) of the square submatrix.
#
# Your task is to flip the submatrix by reversing the order of its rows
# vertically.
#
# Return the updated matrix.
#
# Example 1:
#
# Input: grid = [[1,2,3,4],[5,6,7,8],[9,10,11,12],[13,14,15,16]], x = 1, y
# = 0, k = 3
#
# Output: [[1,2,3,4],[13,14,15,8],[9,10,11,12],[5,6,7,16]]
#
# Explanation:
#
# The diagram above shows the grid before and after the transformation.
#
# Example 2:
#
# ​​​​​​​
#
# Input: grid = [[3,4,2,3],[2,3,4,2]], x = 0, y = 2, k = 2
#
# Output: [[3,4,4,2],[2,3,2,3]]
#
# Explanation:
#
# The diagram above shows the grid before and after the transformation.
#
# Constraints:
#
# m == grid.length
#
# n == grid[i].length
#
# 1 <= m, n <= 50
#
# 1 <= grid[i][j] <= 100
#
# 0 <= x < m
#
# 0 <= y < n
#
# 1 <= k <= min(m - x, n - y)
#

# @lc code=start
from typing import List


class Solution:
    def reverseSubmatrix(self, grid: List[List[int]], x: int, y: int, k: int) -> List[List[int]]:
        """
        Interview explanation:
        Vertically flip a k×k block by swapping rows top↔bottom inside it.

        Algorithm:
        - For row offset t in 0..k//2-1, swap grid[x+t][y:y+k] with
          grid[x+k-1-t][y:y+k].

        Complexity: O(k^2) time, O(1) extra space.
        """
        for t in range(k // 2):
            r1, r2 = x + t, x + k - 1 - t
            for c in range(y, y + k):
                grid[r1][c], grid[r2][c] = grid[r2][c], grid[r1][c]
        return grid

    def reverseSubmatrix_copy(self, grid: List[List[int]], x: int, y: int, k: int) -> List[List[int]]:
        """
        Interview explanation:
        Alternate: extract the block, reverse its rows, write back.

        Algorithm:
        - block = [row[y:y+k] for row in grid[x:x+k]]; reverse; assign.

        Complexity: O(k^2) time and space.
        """
        block = [grid[i][y : y + k][:] for i in range(x, x + k)]
        block.reverse()
        for i, row in enumerate(block):
            grid[x + i][y : y + k] = row
        return grid
# @lc code=end

