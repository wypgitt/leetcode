#
# @lc app=leetcode id=1536 lang=python3
#
# [1536] Minimum Swaps to Arrange a Binary Grid
#
# https://leetcode.com/problems/minimum-swaps-to-arrange-a-binary-grid/description/
#
# algorithms
# Medium (70.24%)
# Likes:    1030
# Dislikes: 108
# Total Accepted:    107K
# Total Submissions: 153K
# Testcase Example:  "[[0,0,1],[1,1,0],[1,0,0]]"
#
# Given an n x n binary grid, in one step you can choose two adjacent rows of
# the grid and swap them.
#
# A grid is said to be valid if all the cells above the main diagonal are
# zeros.
#
# Return the minimum number of steps needed to make the grid valid, or -1 if
# the grid cannot be valid.
#
# The main diagonal of a grid is the diagonal that starts at cell (1, 1) and
# ends at cell (n, n).
#
# Example 1:
#
# Input: grid = [[0,0,1],[1,1,0],[1,0,0]]
# Output: 3
#
# Example 2:
#
# Input: grid = [[0,1,1,0],[0,1,1,0],[0,1,1,0],[0,1,1,0]]
# Output: -1
# Explanation: All rows are similar, swaps have no effect on the grid.
#
# Example 3:
#
# Input: grid = [[1,0,0],[1,1,0],[1,1,1]]
# Output: 0
#
# Constraints:
#
# n == grid.length == grid[i].length
#
# 1 <= n <= 200
#
# grid[i][j] is either 0 or 1
#

# @lc code=start
from typing import List


class Solution:
    def minSwaps(self, grid: List[List[int]]) -> int:
        """
        Interview explanation:
        Arrange rows so grid[i][j]==0 for j>i (enough trailing zeros). Compute
        trailing-zero count per row; greedily for row i find nearest later row
        with zeros>=n-1-i and bubble it up (count swaps).

        Algorithm:
        - zeros[i]=trailing zeros; for need=n-1..0 find j with zeros[j]>=need;
          rotate zeros[i..j]; ans+=j-i.

        Complexity: O(n^2) time, O(n) space.
        """
        n = len(grid)
        zeros = []
        for row in grid:
            z = 0
            for j in range(n - 1, -1, -1):
                if row[j] == 0:
                    z += 1
                else:
                    break
            zeros.append(z)
        ans = 0
        for i in range(n):
            need = n - 1 - i
            j = i
            while j < n and zeros[j] < need:
                j += 1
            if j == n:
                return -1
            ans += j - i
            val = zeros.pop(j)
            zeros.insert(i, val)
        return ans
# @lc code=end
