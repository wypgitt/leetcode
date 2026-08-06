#
# @lc app=leetcode id=1895 lang=python3
#
# [1895] Largest Magic Square
#
# https://leetcode.com/problems/largest-magic-square/description/
#
# algorithms
# Medium (75.19%)
# Likes:    612
# Dislikes: 335
# Total Accepted:    91.0K
# Total Submissions: 121K
# Testcase Example:  "[[7,1,4,5,6],[2,5,1,6,4],[1,5,4,3,2],[1,2,7,3,4]]"
#
# A k x k magic square is a k x k grid filled with integers such that every row
# sum, every column sum, and both diagonal sums are all equal. The integers in
# the magic square do not have to be distinct. Every 1 x 1 grid is trivially a
# magic square.
#
# Given an m x n integer grid, return the size (i.e., the side length k) of the
# largest magic square that can be found within this grid.
#
# Example 1:
#
# Input: grid = [[7,1,4,5,6],[2,5,1,6,4],[1,5,4,3,2],[1,2,7,3,4]]
# Output: 3
# Explanation: The largest magic square has a size of 3.
# Every row sum, column sum, and diagonal sum of this magic square is equal to
# 12.
# - Row sums: 5+1+6 = 5+4+3 = 2+7+3 = 12
# - Column sums: 5+5+2 = 1+4+7 = 6+3+3 = 12
# - Diagonal sums: 5+4+3 = 6+4+2 = 12
#
# Example 2:
#
# Input: grid = [[5,1,3,1],[9,3,3,1],[1,3,3,8]]
# Output: 2
#
# Constraints:
#
# m == grid.length
#
# n == grid[i].length
#
# 1 <= m, n <= 50
#
# 1 <= grid[i][j] <= 10^6
#

# @lc code=start
from typing import List


class Solution:
    def largestMagicSquare(self, grid: List[List[int]]) -> int:
        """
        Interview explanation:
        Largest k where some k×k subgrid has equal row, column, and both
        diagonal sums. Use 2D prefix sums; try k from min(m,n) down to 1.

        Algorithm (prefix sums):
        - row/col prefix for O(1) range sums.
        - For each k, each top-left: check all rows/cols/diags equal.

        Complexity: O(m*n*min(m,n)^2) time, O(m*n) space.
        """
        m, n = len(grid), len(grid[0])
        # pref[i+1][j+1] = sum of grid[:i][:j] wait use row and col prefixes
        row = [[0] * (n + 1) for _ in range(m)]
        col = [[0] * (m + 1) for _ in range(n)]
        for i in range(m):
            for j in range(n):
                row[i][j + 1] = row[i][j] + grid[i][j]
                col[j][i + 1] = col[j][i] + grid[i][j]

        def magic(x: int, y: int, k: int) -> bool:
            target = row[x][y + k] - row[x][y]
            for i in range(x, x + k):
                if row[i][y + k] - row[i][y] != target:
                    return False
            for j in range(y, y + k):
                if col[j][x + k] - col[j][x] != target:
                    return False
            s1 = s2 = 0
            for t in range(k):
                s1 += grid[x + t][y + t]
                s2 += grid[x + t][y + k - 1 - t]
            return s1 == target and s2 == target

        for k in range(min(m, n), 0, -1):
            for i in range(m - k + 1):
                for j in range(n - k + 1):
                    if magic(i, j, k):
                        return k
        return 1
# @lc code=end
