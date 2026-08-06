#
# @lc app=leetcode id=1162 lang=python3
#
# [1162] As Far from Land as Possible
#
# https://leetcode.com/problems/as-far-from-land-as-possible/description/
#
# algorithms
# Medium (52.45%)
# Likes:    4306
# Dislikes: 113
# Total Accepted:    192K
# Total Submissions: 366K
# Testcase Example:  "[[1,0,1],[0,0,0],[1,0,1]]"
#
# Given an n x n grid containing only values 0 and 1, where 0 represents water
# and 1 represents land, find a water cell such that its distance to the
# nearest land cell is maximized, and return the distance. If no land or water
# exists in the grid, return -1.
#
# The distance used in this problem is the Manhattan distance: the distance
# between two cells (x0, y0) and (x1, y1) is |x0 - x1| + |y0 - y1|.
#
# Example 1:
#
# Input: grid = [[1,0,1],[0,0,0],[1,0,1]]
# Output: 2
# Explanation: The cell (1, 1) is as far as possible from all the land with
# distance 2.
#
# Example 2:
#
# Input: grid = [[1,0,0],[0,0,0],[0,0,0]]
# Output: 4
# Explanation: The cell (2, 2) is as far as possible from all the land with
# distance 4.
#
# Constraints:
#
# n == grid.length
#
# n == grid[i].length
#
# 1 <= n <= 100
#
# grid[i][j] is 0 or 1
#

# @lc code=start
from typing import List, Deque, Tuple
from collections import deque


class Solution:
    def maxDistance(self, grid: List[List[int]]) -> int:
        """
        Interview explanation:
        Max Manhattan distance from a water cell (0) to the nearest land (1).
        Multi-source BFS from all lands simultaneously; last water reached is answer.

        Algorithm (multi BFS):
        - Enqueue all lands; BFS expanding to waters; track distance.
        - If no land or no water, return -1; else max dist.

        Complexity: O(n^2) time/space for n x n grid.
        """
        n = len(grid)
        q: Deque[Tuple[int, int]] = deque()
        for i in range(n):
            for j in range(n):
                if grid[i][j] == 1:
                    q.append((i, j))
        if not q or len(q) == n * n:
            return -1

        dist = -1
        dirs = ((1, 0), (-1, 0), (0, 1), (0, -1))
        while q:
            for _ in range(len(q)):
                r, c = q.popleft()
                for dr, dc in dirs:
                    nr, nc = r + dr, c + dc
                    if 0 <= nr < n and 0 <= nc < n and grid[nr][nc] == 0:
                        grid[nr][nc] = 1
                        q.append((nr, nc))
            dist += 1
        return dist
# @lc code=end
