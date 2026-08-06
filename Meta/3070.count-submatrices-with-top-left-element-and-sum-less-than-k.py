#
# @lc app=leetcode id=3070 lang=python3
#
# [3070] Count Submatrices with Top-Left Element and Sum Less Than k
#
# https://leetcode.com/problems/count-submatrices-with-top-left-element-and-sum-less-than-k/description/
#
# algorithms
# Medium (74.94%)
# Likes:    470
# Dislikes: 22
# Total Accepted:    123.8K
# Total Submissions: 165.2K
# Testcase Example:  "[[7,6,3],[6,6,1]]\n18"
#
#
# You are given a 0-indexed integer matrix grid and an integer k.
#
# Return the number of submatrices that contain the top-left element of
# the grid, and have a sum less than or equal to k.
#
# Example 1:
#
# Input: grid = [[7,6,3],[6,6,1]], k = 18
# Output: 4
# Explanation: There are only 4 submatrices, shown in the image above,
# that contain the top-left element of grid, and have a sum less than or
# equal to 18.
#
# Example 2:
#
# Input: grid = [[7,2,9],[1,5,0],[2,6,6]], k = 20
# Output: 6
# Explanation: There are only 6 submatrices, shown in the image above,
# that contain the top-left element of grid, and have a sum less than or
# equal to 20.
#
# Constraints:
#
# m == grid.length
#
# n == grid[i].length
#
# 1 <= n, m <= 1000
#
# 0 <= grid[i][j] <= 1000
#
# 1 <= k <= 10^9
#

# @lc code=start
from typing import List


class Solution:
    def countSubmatrices(self, grid: List[List[int]], k: int) -> int:
        """
        Interview explanation:
        Count submatrices that include cell (0,0) with sum <= k. Those are
        exactly the prefixes grid[0..i][0..j].

        Algorithm:
        - Build 2D prefix sums in place (or on a copy); count prefixes <= k.

        Complexity: O(m*n) time, O(1) extra space (mutates a local row/grid).
        """
        m, n = len(grid), len(grid[0])
        ans = 0
        for i in range(m):
            for j in range(n):
                if i:
                    grid[i][j] += grid[i - 1][j]
                if j:
                    grid[i][j] += grid[i][j - 1]
                if i and j:
                    grid[i][j] -= grid[i - 1][j - 1]
                if grid[i][j] <= k:
                    ans += 1
        return ans

    def countSubmatrices_row(self, grid: List[List[int]], k: int) -> int:
        """
        Interview explanation:
        Alternate without mutating both axes first: maintain running row sums,
        then column-wise prefix of those to get rectangle sums from (0,0).

        Algorithm:
        - For each cell add left neighbor of same row; then add above cell.

        Complexity: O(m*n) time, O(1) extra if mutating grid.
        """
        m, n = len(grid), len(grid[0])
        ans = 0
        for i in range(m):
            for j in range(1, n):
                grid[i][j] += grid[i][j - 1]
        for i in range(m):
            for j in range(n):
                if i:
                    grid[i][j] += grid[i - 1][j]
                if grid[i][j] <= k:
                    ans += 1
        return ans
# @lc code=end
