#
# @lc app=leetcode id=3240 lang=python3
#
# [3240] Minimum Number of Flips to Make Binary Grid Palindromic II
#
# https://leetcode.com/problems/minimum-number-of-flips-to-make-binary-grid-palindromic-ii/description/
#
# algorithms
# Medium (25.82%)
# Likes:    144
# Dislikes: 57
# Total Accepted:    12.8K
# Total Submissions: 49.6K
# Testcase Example:  "[[1,0,0],[0,1,0],[0,0,1]]"
#
#
# You are given an m x n binary matrix grid.
#
# A row or column is considered palindromic if its values read the same
# forward and backward.
#
# You can flip any number of cells in grid from 0 to 1, or from 1 to 0.
#
# Return the minimum number of cells that need to be flipped to make all
# rows and columns palindromic, and the total number of 1's in grid
# divisible by 4.
#
# Example 1:
#
# Input: grid = [[1,0,0],[0,1,0],[0,0,1]]
#
# Output: 3
#
# Explanation:
#
# Example 2:
#
# Input: grid = [[0,1],[0,1],[0,0]]
#
# Output: 2
#
# Explanation:
#
# Example 3:
#
# Input: grid = [[1],[1]]
#
# Output: 2
#
# Explanation:
#
# Constraints:
#
# m == grid.length
#
# n == grid[i].length
#
# 1 <= m * n <= 2 * 10^5
#
# 0 <= grid[i][j] <= 1
#

# @lc code=start
from typing import List


class Solution:
    def minFlips(self, grid: List[List[int]]) -> int:
        """
        Interview explanation:
        All rows and columns palindromic forces 4-cycles in corners to be equal,
        middle-row/col pairs equal, and (if both odd) center 0. Also # of 1s
        must be divisible by 4; middle pairs adjust the residue cheaply.

        Algorithm:
        - For each 4-cell orbit: add min(ones, 4-ones).
        - Center (odd x odd): must flip 1 -> 0.
        - Middle pairs: count mismatches (diff) and matching ones (cnt1);
          add diff if cnt1 % 4 == 0 or diff > 0 else 2.

        Complexity: O(m*n) time, O(1) space.
        Alternate: case-split even/odd dimensions and DP residue of middle ones.
        """
        m, n = len(grid), len(grid[0])
        ans = 0
        for i in range(m // 2):
            for j in range(n // 2):
                ones = (
                    grid[i][j]
                    + grid[i][n - 1 - j]
                    + grid[m - 1 - i][j]
                    + grid[m - 1 - i][n - 1 - j]
                )
                ans += min(ones, 4 - ones)

        if m % 2 and n % 2:
            ans += grid[m // 2][n // 2]

        diff = cnt1 = 0
        if m % 2:
            for j in range(n // 2):
                a, b = grid[m // 2][j], grid[m // 2][n - 1 - j]
                if a == b:
                    cnt1 += a * 2
                else:
                    diff += 1
        if n % 2:
            for i in range(m // 2):
                a, b = grid[i][n // 2], grid[m - 1 - i][n // 2]
                if a == b:
                    cnt1 += a * 2
                else:
                    diff += 1

        ans += diff if cnt1 % 4 == 0 or diff else 2
        return ans

# @lc code=end
