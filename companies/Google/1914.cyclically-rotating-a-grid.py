#
# @lc app=leetcode id=1914 lang=python3
#
# [1914] Cyclically Rotating a Grid
#
# https://leetcode.com/problems/cyclically-rotating-a-grid/description/
#
# algorithms
# Medium (74.02%)
# Likes:    465
# Dislikes: 306
# Total Accepted:    84.5K
# Total Submissions: 114K
# Testcase Example:  "[[40,10],[30,20]]"
#
# You are given an m x n integer matrix grid, where m and n are both even
# integers, and an integer k.
#
# The matrix is composed of several layers, which is shown in the below image,
# where each color is its own layer:
#
# A cyclic rotation of the matrix is done by cyclically rotating each layer in
# the matrix. To cyclically rotate a layer once, each element in the layer will
# take the place of the adjacent element in the counter-clockwise direction. An
# example rotation is shown below:
#
# Return the matrix after applying k cyclic rotations to it.
#
# Example 1:
#
# Input: grid = [[40,10],[30,20]], k = 1
# Output: [[10,20],[40,30]]
# Explanation: The figures above represent the grid at every state.
#
# Example 2:
#
# Input: grid = [[1,2,3,4],[5,6,7,8],[9,10,11,12],[13,14,15,16]], k = 2
# Output: [[3,4,8,12],[2,11,10,16],[1,7,6,15],[5,9,13,14]]
# Explanation: The figures above represent the grid at every state.
#
# Constraints:
#
# m == grid.length
#
# n == grid[i].length
#
# 2 <= m, n <= 50
#
# Both m and n are even integers.
#
# 1 <= grid[i][j] <=^ 5000
#
# 1 <= k <= 10^9
#

# @lc code=start
from typing import List


class Solution:
    def rotateGrid(self, grid: List[List[int]], k: int) -> List[List[int]]:
        """
        Interview explanation:
        Rotate each concentric layer of the grid by k steps counter-clockwise.

        Algorithm:
        - For layer t=0..: extract layer as list (top,right,bottom,left), rotate
          left by k % len, write back.

        Complexity: O(mn) time/space.
        """
        m, n = len(grid), len(grid[0])
        layers = min(m, n) // 2
        for t in range(layers):
            vals = []
            for j in range(t, n - t):
                vals.append(grid[t][j])
            for i in range(t + 1, m - t):
                vals.append(grid[i][n - 1 - t])
            for j in range(n - 2 - t, t - 1, -1):
                vals.append(grid[m - 1 - t][j])
            for i in range(m - 2 - t, t, -1):
                vals.append(grid[i][t])
            L = len(vals)
            if L == 0:
                continue
            r = k % L
            vals = vals[r:] + vals[:r]
            idx = 0
            for j in range(t, n - t):
                grid[t][j] = vals[idx]
                idx += 1
            for i in range(t + 1, m - t):
                grid[i][n - 1 - t] = vals[idx]
                idx += 1
            for j in range(n - 2 - t, t - 1, -1):
                grid[m - 1 - t][j] = vals[idx]
                idx += 1
            for i in range(m - 2 - t, t, -1):
                grid[i][t] = vals[idx]
                idx += 1
        return grid
# @lc code=end
