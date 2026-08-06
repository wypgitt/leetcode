#
# @lc app=leetcode id=3242 lang=python3
#
# [3242] Design Neighbor Sum Service
#
# https://leetcode.com/problems/design-neighbor-sum-service/description/
#
# algorithms
# Easy (76.76%)
# Likes:    117
# Dislikes: 20
# Total Accepted:    48.8K
# Total Submissions: 63.5K
# Testcase Example:  "[\"NeighborSum\",\"adjacentSum\",\"adjacentSum\",\"diagonalSum\",\"diagonalSum\"]\n[[[[0,1,2],[3,4,5],[6,7,8]]],[1],[4],[4],[8]]"
#
#
# You are given a n x n 2D array grid containing distinct elements in the
# range [0, n^2 - 1].
#
# Implement the NeighborSum class:
#
# NeighborSum(int [][]grid) initializes the object.
#
# int adjacentSum(int value) returns the sum of elements which are
# adjacent neighbors of value, that is either to the top, left, right, or
# bottom of value in grid.
#
# int diagonalSum(int value) returns the sum of elements which are
# diagonal neighbors of value, that is either to the top-left, top-right,
# bottom-left, or bottom-right of value in grid.
#
# Example 1:
#
# Input:
#
# ["NeighborSum", "adjacentSum", "adjacentSum", "diagonalSum",
# "diagonalSum"]
#
# [[[[0, 1, 2], [3, 4, 5], [6, 7, 8]]], [1], [4], [4], [8]]
#
# Output: [null, 6, 16, 16, 4]
#
# Explanation:
#
# The adjacent neighbors of 1 are 0, 2, and 4.
#
# The adjacent neighbors of 4 are 1, 3, 5, and 7.
#
# The diagonal neighbors of 4 are 0, 2, 6, and 8.
#
# The diagonal neighbor of 8 is 4.
#
# Example 2:
#
# Input:
#
# ["NeighborSum", "adjacentSum", "diagonalSum"]
#
# [[[[1, 2, 0, 3], [4, 7, 15, 6], [8, 9, 10, 11], [12, 13, 14, 5]]], [15],
# [9]]
#
# Output: [null, 23, 45]
#
# Explanation:
#
# The adjacent neighbors of 15 are 0, 10, 7, and 6.
#
# The diagonal neighbors of 9 are 4, 12, 14, and 15.
#
# Constraints:
#
# 3 <= n == grid.length == grid[0].length <= 10
#
# 0 <= grid[i][j] <= n^2 - 1
#
# All grid[i][j] are distinct.
#
# value in adjacentSum and diagonalSum will be in the range [0, n^2 - 1].
#
# At most 2 * n^2 calls will be made to adjacentSum and diagonalSum.
#

# @lc code=start
from typing import List


class NeighborSum:
    """
    Interview explanation:
    Values are unique, so map each value to its (r, c) once, then sum the four
    orthogonal or four diagonal neighbors on demand.

    Algorithm:
    - __init__: store grid and value -> (r, c).
    - adjacentSum / diagonalSum: walk the four deltas and add in-bounds cells.

    Complexity: O(n^2) init, O(1) per query; O(n^2) space.
    """

    def __init__(self, grid: List[List[int]]):
        self.grid = grid
        self.n = len(grid)
        self.pos = {}
        for i, row in enumerate(grid):
            for j, v in enumerate(row):
                self.pos[v] = (i, j)

    def _sum(self, value: int, deltas: List[tuple]) -> int:
        r, c = self.pos[value]
        total = 0
        for dr, dc in deltas:
            nr, nc = r + dr, c + dc
            if 0 <= nr < self.n and 0 <= nc < self.n:
                total += self.grid[nr][nc]
        return total

    def adjacentSum(self, value: int) -> int:
        """
        Interview explanation:
        Sum of up/down/left/right neighbors of value's cell.

        Algorithm:
        - Look up (r,c); add in-bounds orthogonal neighbors.

        Complexity: O(1) time, O(1) space.
        """
        return self._sum(value, [(-1, 0), (1, 0), (0, -1), (0, 1)])

    def diagonalSum(self, value: int) -> int:
        """
        Interview explanation:
        Sum of four diagonal neighbors of value's cell.

        Algorithm:
        - Look up (r,c); add in-bounds diagonal neighbors.

        Complexity: O(1) time, O(1) space.
        """
        return self._sum(value, [(-1, -1), (-1, 1), (1, -1), (1, 1)])


# Your NeighborSum object will be instantiated and called as such:
# obj = NeighborSum(grid)
# param_1 = obj.adjacentSum(value)
# param_2 = obj.diagonalSum(value)
# @lc code=end
