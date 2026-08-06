#
# @lc app=leetcode id=3905 lang=python3
#
# [3905] Multi Source Flood Fill
#
# https://leetcode.com/problems/multi-source-flood-fill/description/
#
# algorithms
# Medium (55.90%)
# Likes:    96
# Dislikes: 4
# Total Accepted:    26.4K
# Total Submissions: 47.2K
# Testcase Example:  "3\n3\n[[0,0,1],[2,2,2]]"
#
#
# You are given two integers n and m representing the number of rows and
# columns of a grid, respectively.
#
# You are also given a 2D integer array sources, where sources[i] = [r_i,
# c_i, color_​​​​​​​i] indicates that the cell (r_i, c_i) is initially
# colored with color_i. All other cells are initially uncolored and
# represented as 0.
#
# At each time step, every currently colored cell spreads its color to all
# adjacent uncolored cells in the four directions: up, down, left, and
# right. All spreads happen simultaneously.
#
# If multiple colors reach the same uncolored cell at the same time step,
# the cell takes the color with the maximum value.
#
# The process continues until no more cells can be colored.
#
# Return a 2D integer array representing the final state of the grid,
# where each cell contains its final color.
#
# Example 1:
#
# Input: n = 3, m = 3, sources = [[0,0,1],[2,2,2]]
#
# Output: [[1,1,2],[1,2,2],[2,2,2]]
#
# Explanation:
#
# The grid at each time step is as follows:
#
# ​​​​​​​
#
# At time step 2, cells (0, 2), (1, 1), and (2, 0) are reached by both
# colors, so they are assigned color 2 as it has the maximum value among
# them.
#
# Example 2:
#
# Input: n = 3, m = 3, sources = [[0,1,3],[1,1,5]]
#
# Output: [[3,3,3],[5,5,5],[5,5,5]]
#
# Explanation:
#
# The grid at each time step is as follows:
#
# Example 3:
#
# Input: n = 2, m = 2, sources = [[1,1,5]]
#
# Output: [[5,5],[5,5]]
#
# Explanation:
#
# The grid at each time step is as follows:
#
# ​​​​​​​
#
# Since there is only one source, all cells are assigned the same color.
#
# Constraints:
#
# 1 <= n, m <= 10^5
#
# 1 <= n * m <= 10^5
#
# 1 <= sources.length <= n * m
#
# sources[i] = [r_i, c_i, color_i]
#
# 0 <= r_i <= n - 1
#
# 0 <= c_i <= m - 1
#
# 1 <= color_i <= 10^6​​​​​​​
#
# All (r_i, c_i​​​​​​​) in sources are distinct.
#

# @lc code=start
from collections import deque
from typing import List


class Solution:
    def colorGrid(self, n: int, m: int, sources: List[List[int]]) -> List[List[int]]:
        """
        Interview explanation:
        Multi-source BFS flood fill: colors expand simultaneously to adjacent
        uncolored cells; ties at the same time take the max color.

        Algorithm:
        - Seed queue with all sources at distance 0.
        - Each layer collect proposals for uncolored neighbors; keep max color
          per cell, then paint and enqueue winners.

        Complexity: O(n m) time, O(n m) space.
        """
        grid = [[0] * m for _ in range(n)]
        dist = [[-1] * m for _ in range(n)]
        queue = deque()

        for row, col, color in sources:
            grid[row][col] = color
            dist[row][col] = 0
            queue.append((row, col))

        directions = ((1, 0), (-1, 0), (0, 1), (0, -1))
        time = 0

        while queue:
            proposals = {}

            for _ in range(len(queue)):
                row, col = queue.popleft()
                color = grid[row][col]

                for dr, dc in directions:
                    nr = row + dr
                    nc = col + dc
                    if 0 <= nr < n and 0 <= nc < m and dist[nr][nc] == -1:
                        key = nr * m + nc
                        if color > proposals.get(key, 0):
                            proposals[key] = color

            time += 1
            for key, color in proposals.items():
                row, col = divmod(key, m)
                if dist[row][col] == -1:
                    dist[row][col] = time
                    grid[row][col] = color
                    queue.append((row, col))

        return grid
# @lc code=end
