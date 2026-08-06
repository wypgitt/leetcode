#
# @lc app=leetcode id=317 lang=python3
#
# [317] Shortest Distance from All Buildings
#
# https://leetcode.com/problems/shortest-distance-from-all-buildings/description/
#
# algorithms
# Hard (44.97%)
# Likes:    1993
# Dislikes: 342
# Total Accepted:    221.7K
# Total Submissions: 492.9K
# Testcase Example:  "[[1,0,2,0,1],[0,0,0,0,0],[0,0,1,0,0]]"
#
#
# You are given an m x n grid grid of values 0, 1, or 2, where:
#
# each 0 marks an empty land that you can pass by freely,
#
# each 1 marks a building that you cannot pass through, and
#
# each 2 marks an obstacle that you cannot pass through.
#
# You want to build a house on an empty land that reaches all buildings in
# the shortest total travel distance. You can only move up, down, left,
# and right.
#
# Return the shortest travel distance for such a house. If it is not
# possible to build such a house according to the above rules, return -1.
#
# The total travel distance is the sum of the distances between the houses
# of the friends and the meeting point.
#
# Example 1:
#
# Input: grid = [[1,0,2,0,1],[0,0,0,0,0],[0,0,1,0,0]]
# Output: 7
# Explanation: Given three buildings at (0,0), (0,4), (2,2), and an
# obstacle at (0,2).
# The point (1,2) is an ideal empty land to build a house, as the total
# travel distance of 3+3+1=7 is minimal.
# So return 7.
#
# Example 2:
#
# Input: grid = [[1,0]]
# Output: 1
#
# Example 3:
#
# Input: grid = [[1]]
# Output: -1
#
# Constraints:
#
# m == grid.length
#
# n == grid[i].length
#
# 1 <= m, n <= 50
#
# grid[i][j] is either 0, 1, or 2.
#
# There will be at least one building in the grid.
#
# @lc code=start
from collections import deque
from typing import List


class Solution:
    def shortestDistance(self, grid: List[List[int]]) -> int:
        """
        Interview explanation:
        Empty land (0) distance sum to all buildings (1); walls are 2.
        Multi BFS: from each building, accumulate distance into empty cells and
        count how many buildings reached each cell. Answer = min sum among cells
        reachable from all buildings.

        Complexity: O(B * m * n) time, O(m n) space.
        """
        if not grid or not grid[0]:
            return -1
        m, n = len(grid), len(grid[0])
        dist = [[0] * n for _ in range(m)]
        reach = [[0] * n for _ in range(m)]
        buildings = 0

        for i in range(m):
            for j in range(n):
                if grid[i][j] != 1:
                    continue
                buildings += 1
                q = deque([(i, j, 0)])
                seen = [[False] * n for _ in range(m)]
                seen[i][j] = True
                while q:
                    r, c, d = q.popleft()
                    for dr, dc in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                        nr, nc = r + dr, c + dc
                        if (
                            0 <= nr < m
                            and 0 <= nc < n
                            and not seen[nr][nc]
                            and grid[nr][nc] == 0
                        ):
                            seen[nr][nc] = True
                            dist[nr][nc] += d + 1
                            reach[nr][nc] += 1
                            q.append((nr, nc, d + 1))

        ans = float("inf")
        for i in range(m):
            for j in range(n):
                if grid[i][j] == 0 and reach[i][j] == buildings:
                    ans = min(ans, dist[i][j])
        return -1 if ans == float("inf") else ans
# @lc code=end

