#
# @lc app=leetcode id=308 lang=python3
#
# [308] Range Sum Query 2D - Mutable
#
# https://leetcode.com/problems/range-sum-query-2d-mutable/description/
#
# algorithms
# Medium (45.55%)
# Likes:    823
# Dislikes: 97
# Total Accepted:    84.3K
# Total Submissions: 185.1K
# Testcase Example:  "[\"NumMatrix\",\"sumRegion\",\"update\",\"sumRegion\"]\n[[[[3,0,1,4,2],[5,6,3,2,1],[1,2,0,1,5],[4,1,0,1,7],[1,0,3,0,5]]],[2,1,4,3],[3,2,2],[2,1,4,3]]"
#
#
# Given a 2D matrix matrix, handle multiple queries of the following
# types:
#
# Update the value of a cell in matrix.
#
# Calculate the sum of the elements of matrix inside the rectangle defined
# by its upper left corner (row1, col1) and lower right corner (row2,
# col2).
#
# Implement the NumMatrix class:
#
# NumMatrix(int[][] matrix) Initializes the object with the integer matrix
# matrix.
#
# void update(int row, int col, int val) Updates the value of
# matrix[row][col] to be val.
#
# int sumRegion(int row1, int col1, int row2, int col2) Returns the sum of
# the elements of matrix inside the rectangle defined by its upper left
# corner (row1, col1) and lower right corner (row2, col2).
#
# Example 1:
#
# Input
# ["NumMatrix", "sumRegion", "update", "sumRegion"]
# [[[[3, 0, 1, 4, 2], [5, 6, 3, 2, 1], [1, 2, 0, 1, 5], [4, 1, 0, 1, 7],
# [1, 0, 3, 0, 5]]], [2, 1, 4, 3], [3, 2, 2], [2, 1, 4, 3]]
# Output
# [null, 8, null, 10]
#
# Explanation
# NumMatrix numMatrix = new NumMatrix([[3, 0, 1, 4, 2], [5, 6, 3, 2, 1],
# [1, 2, 0, 1, 5], [4, 1, 0, 1, 7], [1, 0, 3, 0, 5]]);
# numMatrix.sumRegion(2, 1, 4, 3); // return 8 (i.e. sum of the left red
# rectangle)
# numMatrix.update(3, 2, 2);       // matrix changes from left image to
# right image
# numMatrix.sumRegion(2, 1, 4, 3); // return 10 (i.e. sum of the right red
# rectangle)
#
# Constraints:
#
# m == matrix.length
#
# n == matrix[i].length
#
# 1 <= m, n <= 200
#
# -1000 <= matrix[i][j] <= 1000
#
# 0 <= row < m
#
# 0 <= col < n
#
# -1000 <= val <= 1000
#
# 0 <= row1 <= row2 < m
#
# 0 <= col1 <= col2 < n
#
# At most 5000 calls will be made to sumRegion and update.
#
# @lc code=start
from typing import List


class NumMatrix:
    def __init__(self, matrix: List[List[int]]):
        """
        Interview explanation:
        2D Binary Indexed Tree: update/query rectangles in O(log m log n).
        Store original matrix to compute deltas on update.

        Algorithm:
        - mat zeros + bit (m+1)×(n+1); call update for each matrix[i][j].

        Complexity: O(mn log m log n) build, O(log m log n) update/query.
        """
        if not matrix or not matrix[0]:
            self.m = self.n = 0
            return
        self.m, self.n = len(matrix), len(matrix[0])
        self.mat = [[0] * self.n for _ in range(self.m)]
        self.bit = [[0] * (self.n + 1) for _ in range(self.m + 1)]
        for i in range(self.m):
            for j in range(self.n):
                self.update(i, j, matrix[i][j])

    def _add(self, r: int, c: int, delta: int) -> None:
        i = r + 1
        while i <= self.m:
            j = c + 1
            while j <= self.n:
                self.bit[i][j] += delta
                j += j & -j
            i += i & -i

    def _sum(self, r: int, c: int) -> int:
        s, i = 0, r + 1
        while i > 0:
            j = c + 1
            while j > 0:
                s += self.bit[i][j]
                j -= j & -j
            i -= i & -i
        return s

    def update(self, row: int, col: int, val: int) -> None:
        """
        Interview explanation:
        Point update on 2D BIT: apply delta = val - old at (row, col).

        Algorithm:
        - delta = val - mat[row][col]; store new val; _add(row, col, delta).

        Complexity: O(log m log n) time, O(1) extra space.
        """
        if self.m == 0:
            return
        delta = val - self.mat[row][col]
        self.mat[row][col] = val
        self._add(row, col, delta)

    def sumRegion(self, row1: int, col1: int, row2: int, col2: int) -> int:
        """
        Interview explanation:
        Rectangle sum via inclusion-exclusion of four 2D BIT prefix sums.

        Algorithm:
        - _sum(r2,c2) - _sum(r1-1,c2) - _sum(r2,c1-1) + _sum(r1-1,c1-1).

        Complexity: O(log m log n) time, O(1) space.
        """
        return (
            self._sum(row2, col2)
            - self._sum(row1 - 1, col2)
            - self._sum(row2, col1 - 1)
            + self._sum(row1 - 1, col1 - 1)
        )


# Your NumMatrix object will be instantiated and called as such:
# obj = NumMatrix(matrix)
# obj.update(row,col,val)
# param_2 = obj.sumRegion(row1,col1,row2,col2)
# @lc code=end

