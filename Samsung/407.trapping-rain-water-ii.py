#
# @lc app=leetcode id=407 lang=python3
#
# [407] Trapping Rain Water II
#
# https://leetcode.com/problems/trapping-rain-water-ii/description/
#
# algorithms
# Hard (64.17%)
# Likes:    5030
# Dislikes: 176
# Total Accepted:    272K
# Total Submissions: 424K
# Testcase Example:  "[[1,4,3,1,3,2],[3,2,1,3,2,4],[2,3,3,2,3,1]]"
#
# Given an m x n integer matrix heightMap representing the height of each unit
# cell in a 2D elevation map, return the volume of water it can trap after
# raining.
#
# Example 1:
#
# Input: heightMap = [[1,4,3,1,3,2],[3,2,1,3,2,4],[2,3,3,2,3,1]]
# Output: 4
# Explanation: After the rain, water is trapped between the blocks.
# We have two small ponds 1 and 3 units trapped.
# The total volume of water trapped is 4.
#
# Example 2:
#
# Input: heightMap =
# [[3,3,3,3,3],[3,2,2,2,3],[3,2,1,2,3],[3,2,2,2,3],[3,3,3,3,3]]
# Output: 10
#
# Constraints:
#
# m == heightMap.length
#
# n == heightMap[i].length
#
# 1 <= m, n <= 200
#
# 0 <= heightMap[i][j] <= 2 * 10^4
#

# @lc code=start

import heapq
from typing import List


class Solution:
    def trapRainWater(self, heightMap: List[List[int]]) -> int:
        """
        Interview explanation:
        Multisource Dijkstra/BFS on a min-heap of boundary cells. Water level
        at a cell is max(boundary height along best path). Water trapped =
        max(0, water_level - height). Expand inward from lowest boundary.

        Algorithm:
        - Push all border cells into min-heap; mark visited.
        - Pop lowest; for each unvisited neighbor, trap max(0, h-height), push
          neighbor with height max(h, neighbor_height).

        Complexity: O(mn log(mn)) time, O(mn) space.
        """
        if not heightMap or not heightMap[0]:
            return 0
        m, n = len(heightMap), len(heightMap[0])
        if m < 3 or n < 3:
            return 0
        visited = [[False] * n for _ in range(m)]
        heap = []
        for i in range(m):
            for j in range(n):
                if i == 0 or i == m - 1 or j == 0 or j == n - 1:
                    heapq.heappush(heap, (heightMap[i][j], i, j))
                    visited[i][j] = True
        water = 0
        dirs = ((1, 0), (-1, 0), (0, 1), (0, -1))
        while heap:
            h, r, c = heapq.heappop(heap)
            for dr, dc in dirs:
                nr, nc = r + dr, c + dc
                if 0 <= nr < m and 0 <= nc < n and not visited[nr][nc]:
                    visited[nr][nc] = True
                    nh = heightMap[nr][nc]
                    if h > nh:
                        water += h - nh
                    heapq.heappush(heap, (max(h, nh), nr, nc))
        return water
# @lc code=end
