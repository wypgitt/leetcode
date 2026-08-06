#
# @lc app=leetcode id=2482 lang=python3
#
# [2482] Difference Between Ones and Zeros in Row and Column
#
# https://leetcode.com/problems/difference-between-ones-and-zeros-in-row-and-column/description/
#
# algorithms
# Medium (84.57%)
# Likes:    1255
# Dislikes: 86
# Total Accepted:    150.2K
# Total Submissions: 177.6K
# Testcase Example:  "[[0,1,1],[1,0,1],[0,0,1]]"
#
# You are given a 0-indexed m x n binary matrix grid.
#
# A 0-indexed m x n difference matrix diff is created with the following
# procedure:
#
#
# Let the number of ones in the i^th row be onesRow_i.
#
#
# Let the number of ones in the j^th column be onesCol_j.
#
#
# Let the number of zeros in the i^th row be zerosRow_i.
#
#
# Let the number of zeros in the j^th column be zerosCol_j.
#
#
# diff[i][j] = onesRow_i + onesCol_j - zerosRow_i - zerosCol_j
#
# Return the difference matrix diff.
#
#
#
# Example 1:
#
# Input: grid = [[0,1,1],[1,0,1],[0,0,1]]
# Output: [[0,0,4],[0,0,4],[-2,-2,2]]
# Explanation:
# - diff[0][0] = onesRow_0 + onesCol_0 - zerosRow_0 - zerosCol_0 = 2 + 1 - 1 - 2
# = 0
# - diff[0][1] = onesRow_0 + onesCol_1 - zerosRow_0 - zerosCol_1 = 2 + 1 - 1 - 2
# = 0
# - diff[0][2] = onesRow_0 + onesCol_2 - zerosRow_0 - zerosCol_2 = 2 + 3 - 1 - 0
# = 4
# - diff[1][0] = onesRow_1 + onesCol_0 - zerosRow_1 - zerosCol_0 = 2 + 1 - 1 - 2
# = 0
# - diff[1][1] = onesRow_1 + onesCol_1 - zerosRow_1 - zerosCol_1 = 2 + 1 - 1 - 2
# = 0
# - diff[1][2] = onesRow_1 + onesCol_2 - zerosRow_1 - zerosCol_2 = 2 + 3 - 1 - 0
# = 4
# - diff[2][0] = onesRow_2 + onesCol_0 - zerosRow_2 - zerosCol_0 = 1 + 1 - 2 - 2
# = -2
# - diff[2][1] = onesRow_2 + onesCol_1 - zerosRow_2 - zerosCol_1 = 1 + 1 - 2 - 2
# = -2
# - diff[2][2] = onesRow_2 + onesCol_2 - zerosRow_2 - zerosCol_2 = 1 + 3 - 2 - 0
# = 2
#
# Example 2:
#
# Input: grid = [[1,1,1],[1,1,1]]
# Output: [[5,5,5],[5,5,5]]
# Explanation:
# - diff[0][0] = onesRow_0 + onesCol_0 - zerosRow_0 - zerosCol_0 = 3 + 2 - 0 - 0
# = 5
# - diff[0][1] = onesRow_0 + onesCol_1 - zerosRow_0 - zerosCol_1 = 3 + 2 - 0 - 0
# = 5
# - diff[0][2] = onesRow_0 + onesCol_2 - zerosRow_0 - zerosCol_2 = 3 + 2 - 0 - 0
# = 5
# - diff[1][0] = onesRow_1 + onesCol_0 - zerosRow_1 - zerosCol_0 = 3 + 2 - 0 - 0
# = 5
# - diff[1][1] = onesRow_1 + onesCol_1 - zerosRow_1 - zerosCol_1 = 3 + 2 - 0 - 0
# = 5
# - diff[1][2] = onesRow_1 + onesCol_2 - zerosRow_1 - zerosCol_2 = 3 + 2 - 0 - 0
# = 5
#
#
#
# Constraints:
#
#
# m == grid.length
#
#
# n == grid[i].length
#
#
# 1 <= m, n <= 10^5
#
#
# 1 <= m * n <= 10^5
#
#
# grid[i][j] is either 0 or 1.
#

# @lc code=start
from typing import List


class Solution:
    def onesMinusZeros(self, grid: List[List[int]]) -> List[List[int]]:
        """
        Interview explanation:
        diff[i][j] = onesRow_i + onesCol_j - zerosRow_i - zerosCol_j.

        Algorithm:
        - Precompute row/col ones; zeros = len - ones; fill formula
          = 2*(onesRow+onesCol) - m - n.

        Complexity: O(m n) time, O(m+n) space.
        """
        m, n = len(grid), len(grid[0])
        row = [sum(r) for r in grid]
        col = [sum(grid[i][j] for i in range(m)) for j in range(n)]
        return [
            [2 * (row[i] + col[j]) - m - n for j in range(n)] for i in range(m)
        ]
# @lc code=end

