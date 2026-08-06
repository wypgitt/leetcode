#
# @lc app=leetcode id=861 lang=python3
#
# [861] Score After Flipping Matrix
#
# https://leetcode.com/problems/score-after-flipping-matrix/description/
#
# algorithms
# Medium (80.27%)
# Likes:    2508
# Dislikes: 226
# Total Accepted:    171K
# Total Submissions: 213K
# Testcase Example:  "[[0,0,1,1],[1,0,1,0],[1,1,0,0]]"
#
# You are given an m x n binary matrix grid.
#
# A move consists of choosing any row or column and toggling each value in that
# row or column (i.e., changing all 0's to 1's, and all 1's to 0's).
#
# Every row of the matrix is interpreted as a binary number, and the score of
# the matrix is the sum of these numbers.
#
# Return the highest possible score after making any number of moves (including
# zero moves).
#
# Example 1:
#
# Input: grid = [[0,0,1,1],[1,0,1,0],[1,1,0,0]]
# Output: 39
# Explanation: 0b1111 + 0b1001 + 0b1111 = 15 + 9 + 15 = 39
#
# Example 2:
#
# Input: grid = [[0]]
# Output: 1
#
# Constraints:
#
# m == grid.length
#
# n == grid[i].length
#
# 1 <= m, n <= 20
#
# grid[i][j] is either 0 or 1.
#

# @lc code=start
from typing import List


class Solution:
    def matrixScore(self, grid: List[List[int]]) -> int:
        """
        Interview explanation:
        Maximize binary row-sum score via toggles. Make each row's MSB 1 by a
        row flip if needed, then for each lower bit flip the column iff that
        yields more 1s than 0s (greedy; toggles commute).

        Algorithm:
        - Assume row flips so grid[i][0]==1 (or track without mutating).
        - For col j: count ones after implied row flips; take max(ones, m-ones)
          * 2^(n-1-j); add.

        Complexity: O(m*n) time, O(1) extra space.
        """
        m, n = len(grid), len(grid[0])
        ans = m * (1 << (n - 1))
        for j in range(1, n):
            ones = 0
            for i in range(m):
                # after forcing MSB=1 via row flip when grid[i][0]==0
                ones += grid[i][j] if grid[i][0] == 1 else 1 - grid[i][j]
            ans += max(ones, m - ones) * (1 << (n - 1 - j))
        return ans

    def matrixScore_mutate(self, grid: List[List[int]]) -> int:
        """
        Interview explanation:
        Alternate: explicitly flip rows then columns, then sum binary values.

        Algorithm:
        - Flip each row with leading 0. Flip each col with more 0s than 1s.
        - Score = sum of each row as binary.

        Complexity: O(m*n) time, O(1) extra (mutates input).
        """
        m, n = len(grid), len(grid[0])
        for i in range(m):
            if grid[i][0] == 0:
                for j in range(n):
                    grid[i][j] ^= 1
        for j in range(1, n):
            ones = sum(grid[i][j] for i in range(m))
            if ones < m - ones:
                for i in range(m):
                    grid[i][j] ^= 1
        ans = 0
        for i in range(m):
            val = 0
            for j in range(n):
                val = (val << 1) | grid[i][j]
            ans += val
        return ans
# @lc code=end

