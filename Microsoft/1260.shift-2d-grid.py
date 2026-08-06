#
# @lc app=leetcode id=1260 lang=python3
#
# [1260] Shift 2D Grid
#
# https://leetcode.com/problems/shift-2d-grid/description/
#
# algorithms
# Easy (74.47%)
# Likes:    2044
# Dislikes: 373
# Total Accepted:    250K
# Total Submissions: 335K
# Testcase Example:  "[[1,2,3],[4,5,6],[7,8,9]]"
#
# Given a 2D grid of size m x n and an integer k. You need to shift the grid k
# times.
#
# In one shift operation:
#
# Element at grid[i][j] moves to grid[i][j + 1].
#
# Element at grid[i][n - 1] moves to grid[i + 1][0].
#
# Element at grid[m - 1][n - 1] moves to grid[0][0].
#
# Return the 2D grid after applying shift operation k times.
#
# Example 1:
#
# Input: grid = [[1,2,3],[4,5,6],[7,8,9]], k = 1
# Output: [[9,1,2],[3,4,5],[6,7,8]]
#
# Example 2:
#
# Input: grid = [[3,8,1,9],[19,7,2,5],[4,6,11,10],[12,0,21,13]], k = 4
# Output: [[12,0,21,13],[3,8,1,9],[19,7,2,5],[4,6,11,10]]
#
# Example 3:
#
# Input: grid = [[1,2,3],[4,5,6],[7,8,9]], k = 9
# Output: [[1,2,3],[4,5,6],[7,8,9]]
#
# Constraints:
#
# m == grid.length
#
# n == grid[i].length
#
# 1 <= m <= 50
#
# 1 <= n <= 50
#
# -1000 <= grid[i][j] <= 1000
#
# 0 <= k <= 100
#

# @lc code=start

from typing import List


class Solution:
    def shiftGrid(self, grid: List[List[int]], k: int) -> List[List[int]]:
        """
        Interview explanation:
        Flatten m*n grid to 1D, rotate right by k % (m*n), write back. Each
        shift moves (i,j)->(i,j+1) with wrap to next row / (0,0).

        Algorithm:
        - flat = [grid[i][j]...]; n=len(flat); k%=n.
        - flat = flat[-k:]+flat[:-k] (if k else same).
        - Refill grid from flat.

        Complexity: O(m*n) time and space.
        """
        m, n = len(grid), len(grid[0])
        flat = [grid[i][j] for i in range(m) for j in range(n)]
        total = m * n
        k %= total
        if k:
            flat = flat[-k:] + flat[:-k]
        idx = 0
        for i in range(m):
            for j in range(n):
                grid[i][j] = flat[idx]
                idx += 1
        return grid

    def shiftGrid_map(self, grid: List[List[int]], k: int) -> List[List[int]]:
        """
        Interview explanation:
        Alternate: map each index (i*n+j+k)%(m*n) into new grid without
        mutating via temporary.

        Algorithm:
        - Create empty; for each cell place at (pos+k)%total coordinates.

        Complexity: O(m*n) time and space.
        """
        m, n = len(grid), len(grid[0])
        total = m * n
        k %= total
        ans = [[0] * n for _ in range(m)]
        for i in range(m):
            for j in range(n):
                pos = (i * n + j + k) % total
                ans[pos // n][pos % n] = grid[i][j]
        return ans
# @lc code=end
