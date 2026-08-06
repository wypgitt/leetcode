#
# @lc app=leetcode id=2290 lang=python3
#
# [2290] Minimum Obstacle Removal to Reach Corner
#
# https://leetcode.com/problems/minimum-obstacle-removal-to-reach-corner/description/
#
# algorithms
# Hard (70.96%)
# Likes:    1710
# Dislikes: 29
# Total Accepted:    128.8K
# Total Submissions: 181.5K
# Testcase Example:  "[[0,1,1],[1,1,0],[1,1,0]]"
#
# You are given a 0-indexed 2D integer array grid of size m x n. Each cell has
# one of two values:
#
#
# 0 represents an empty cell,
#
#
# 1 represents an obstacle that may be removed.
#
# You can move up, down, left, or right from and to an empty cell.
#
# Return the minimum number of obstacles to remove so you can move from the
# upper left corner (0, 0) to the lower right corner (m - 1, n - 1).
#
#
#
# Example 1:
#
# Input: grid = [[0,1,1],[1,1,0],[1,1,0]]
# Output: 2
# Explanation: We can remove the obstacles at (0, 1) and (0, 2) to create a path
# from (0, 0) to (2, 2).
# It can be shown that we need to remove at least 2 obstacles, so we return 2.
# Note that there may be other ways to remove 2 obstacles to create a path.
#
# Example 2:
#
# Input: grid = [[0,1,0,0,0],[0,1,0,1,0],[0,0,0,1,0]]
# Output: 0
# Explanation: We can move from (0, 0) to (2, 4) without removing any obstacles,
# so we return 0.
#
#
#
# Constraints:
#
#
# m == grid.length
#
#
# n == grid[i].length
#
#
# 1 <= m, n <= 10^5
#
#
# 2 <= m * n <= 10^5
#
#
# grid[i][j] is either 0 or 1.
#
#
# grid[0][0] == grid[m - 1][n - 1] == 0
#

# @lc code=start
from typing import List
from collections import deque


class Solution:
    def minimumObstacles(self, grid: List[List[int]]) -> int:
        """
        Interview explanation:
        0 empty / 1 obstacle; min obstacles to remove to go (0,0)->(m-1,n-1) 4-dir.

        Algorithm:
        - 0-1 BFS: edge cost = grid[nr][nc]; deque push front for 0, back for 1.

        Complexity: O(m*n) time, O(m*n) space.
        """
        m, n = len(grid), len(grid[0])
        dist = [[float("inf")] * n for _ in range(m)]
        dist[0][0] = 0
        dq = deque([(0, 0)])
        while dq:
            r, c = dq.popleft()
            if r == m - 1 and c == n - 1:
                return dist[r][c]
            for dr, dc in ((0, 1), (0, -1), (1, 0), (-1, 0)):
                nr, nc = r + dr, c + dc
                if 0 <= nr < m and 0 <= nc < n:
                    nd = dist[r][c] + grid[nr][nc]
                    if nd < dist[nr][nc]:
                        dist[nr][nc] = nd
                        if grid[nr][nc] == 0:
                            dq.appendleft((nr, nc))
                        else:
                            dq.append((nr, nc))
        return dist[m - 1][n - 1]


    def minimumObstacles_dijkstra(self, grid: List[List[int]]) -> int:
        """
        Interview explanation:
        Classic Dijkstra alternate treating obstacle cells as cost-1 edges.

        Algorithm:
        - Priority queue on (cost,r,c); relax 4-neighbors with +grid[nr][nc].

        Complexity: O(mn log(mn)) time, O(mn) space.
        """
        import heapq
        m, n = len(grid), len(grid[0])
        dist = [[float("inf")] * n for _ in range(m)]
        dist[0][0] = 0
        pq = [(0, 0, 0)]
        while pq:
            d, r, c = heapq.heappop(pq)
            if d != dist[r][c]:
                continue
            if r == m - 1 and c == n - 1:
                return d
            for dr, dc in ((0, 1), (0, -1), (1, 0), (-1, 0)):
                nr, nc = r + dr, c + dc
                if 0 <= nr < m and 0 <= nc < n:
                    nd = d + grid[nr][nc]
                    if nd < dist[nr][nc]:
                        dist[nr][nc] = nd
                        heapq.heappush(pq, (nd, nr, nc))
        return dist[m - 1][n - 1]

# @lc code=end
