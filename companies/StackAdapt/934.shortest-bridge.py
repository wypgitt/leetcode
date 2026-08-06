#
# @lc app=leetcode id=934 lang=python3
#
# [934] Shortest Bridge
#
# https://leetcode.com/problems/shortest-bridge/description/
#
# algorithms
# Medium (59.67%)
# Likes:    5835
# Dislikes: 221
# Total Accepted:    285K
# Total Submissions: 477K
# Testcase Example:  "[[0,1],[1,0]]"
#
# You are given an n x n binary matrix grid where 1 represents land and 0
# represents water.
#
# An island is a 4-directionally connected group of 1's not connected to any
# other 1's. There are exactly two islands in grid.
#
# You may change 0's to 1's to connect the two islands to form one island.
#
# Return the smallest number of 0's you must flip to connect the two islands.
#
# Example 1:
#
# Input: grid = [[0,1],[1,0]]
# Output: 1
#
# Example 2:
#
# Input: grid = [[0,1,0],[0,0,0],[0,0,1]]
# Output: 2
#
# Example 3:
#
# Input: grid = [[1,1,1,1,1],[1,0,0,0,1],[1,0,1,0,1],[1,0,0,0,1],[1,1,1,1,1]]
# Output: 1
#
# Constraints:
#
# n == grid.length == grid[i].length
#
# 2 <= n <= 100
#
# grid[i][j] is either 0 or 1.
#
# There are exactly two islands in grid.
#

# @lc code=start
from collections import deque
from typing import List


class Solution:
    def shortestBridge(self, grid: List[List[int]]) -> int:
        """
        Interview explanation:
        Two islands of 1s. DFS-paint one island, collecting its cells into a
        queue; BFS outward over water until hitting the other island — distance
        is the number of 0s flipped (bridge length).

        Algorithm (DFS paint + BFS):
        - Find first 1; DFS mark island as 2 and enqueue all its cells
        - BFS multi-source; each water step increases dist; first hit of 1 → return dist

        Complexity: O(n^2) time/space for n x n grid.
        """
        n = len(grid)
        q = deque()
        dirs = ((1, 0), (-1, 0), (0, 1), (0, -1))

        def dfs(i: int, j: int) -> None:
            grid[i][j] = 2
            q.append((i, j))
            for di, dj in dirs:
                ni, nj = i + di, j + dj
                if 0 <= ni < n and 0 <= nj < n and grid[ni][nj] == 1:
                    dfs(ni, nj)

        found = False
        for i in range(n):
            if found:
                break
            for j in range(n):
                if grid[i][j] == 1:
                    dfs(i, j)
                    found = True
                    break

        dist = 0
        while q:
            for _ in range(len(q)):
                i, j = q.popleft()
                for di, dj in dirs:
                    ni, nj = i + di, j + dj
                    if 0 <= ni < n and 0 <= nj < n:
                        if grid[ni][nj] == 1:
                            return dist
                        if grid[ni][nj] == 0:
                            grid[ni][nj] = 2
                            q.append((ni, nj))
            dist += 1
        return -1
# @lc code=end

