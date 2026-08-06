#
# @lc app=leetcode id=1368 lang=python3
#
# [1368] Minimum Cost to Make at Least One Valid Path in a Grid
#
# https://leetcode.com/problems/minimum-cost-to-make-at-least-one-valid-path-in-a-grid/description/
#
# algorithms
# Hard (71.12%)
# Likes:    2630
# Dislikes: 36
# Total Accepted:    173K
# Total Submissions: 243K
# Testcase Example:  "[[1,1,1,1],[2,2,2,2],[1,1,1,1],[2,2,2,2]]"
#
# Given an m x n grid. Each cell of the grid has a sign pointing to the next
# cell you should visit if you are currently in this cell. The sign of
# grid[i][j] can be:
#
# 1 which means go to the cell to the right. (i.e go from grid[i][j] to
# grid[i][j + 1])
#
# 2 which means go to the cell to the left. (i.e go from grid[i][j] to
# grid[i][j - 1])
#
# 3 which means go to the lower cell. (i.e go from grid[i][j] to grid[i +
# 1][j])
#
# 4 which means go to the upper cell. (i.e go from grid[i][j] to grid[i -
# 1][j])
#
# Notice that there could be some signs on the cells of the grid that point
# outside the grid.
#
# You will initially start at the upper left cell (0, 0). A valid path in the
# grid is a path that starts from the upper left cell (0, 0) and ends at the
# bottom-right cell (m - 1, n - 1) following the signs on the grid. The valid
# path does not have to be the shortest.
#
# You can modify the sign on a cell with cost = 1. You can modify the sign on a
# cell one time only.
#
# Return the minimum cost to make the grid have at least one valid path.
#
# Example 1:
#
# Input: grid = [[1,1,1,1],[2,2,2,2],[1,1,1,1],[2,2,2,2]]
# Output: 3
# Explanation: You will start at point (0, 0).
# The path to (3, 3) is as follows. (0, 0) --> (0, 1) --> (0, 2) --> (0, 3)
# change the arrow to down with cost = 1 --> (1, 3) --> (1, 2) --> (1, 1) -->
# (1, 0) change the arrow to down with cost = 1 --> (2, 0) --> (2, 1) --> (2,
# 2) --> (2, 3) change the arrow to down with cost = 1 --> (3, 3)
# The total cost = 3.
#
# Example 2:
#
# Input: grid = [[1,1,3],[3,2,2],[1,1,4]]
# Output: 0
# Explanation: You can follow the path from (0, 0) to (2, 2).
#
# Example 3:
#
# Input: grid = [[1,2],[4,3]]
# Output: 1
#
# Constraints:
#
# m == grid.length
#
# n == grid[i].length
#
# 1 <= m, n <= 100
#
# 1 <= grid[i][j] <= 4
#

# @lc code=start

from collections import deque
from typing import List
import heapq


class Solution:
    def minCost(self, grid: List[List[int]]) -> int:
        """
        Interview explanation:
        Signs point R/L/D/U (1-4). Following the sign costs 0; changing costs 1.
        Classic 0-1 BFS (deque): cost-0 edges appendleft, cost-1 append.

        Algorithm:
        - dirs=(0,1),(0,-1),(1,0),(-1,0)
        - dist[][]=inf; deque (0,0) cost 0
        - For each neighbor: nc = cost + (0 if dir matches sign else 1)

        Complexity: O(mn) time, O(mn) space.
        """
        m, n = len(grid), len(grid[0])
        dirs = [(0, 1), (0, -1), (1, 0), (-1, 0)]
        dist = [[10**9] * n for _ in range(m)]
        dist[0][0] = 0
        dq = deque([(0, 0)])
        while dq:
            r, c = dq.popleft()
            for i, (dr, dc) in enumerate(dirs):
                nr, nc = r + dr, c + dc
                if 0 <= nr < m and 0 <= nc < n:
                    cost = dist[r][c] + (0 if grid[r][c] == i + 1 else 1)
                    if cost < dist[nr][nc]:
                        dist[nr][nc] = cost
                        if grid[r][c] == i + 1:
                            dq.appendleft((nr, nc))
                        else:
                            dq.append((nr, nc))
        return dist[m - 1][n - 1]

    def minCost_dijkstra(self, grid: List[List[int]]) -> int:
        """
        Interview explanation:
        Alternate Dijkstra on the same 0/1 edge-weight graph (works but slower
        log factor than 0-1 BFS).

        Algorithm:
        - Min-heap (cost,r,c); relax 4 neighbors with +0/+1

        Complexity: O(mn log(mn)) time, O(mn) space.
        """
        m, n = len(grid), len(grid[0])
        dirs = [(0, 1), (0, -1), (1, 0), (-1, 0)]
        dist = [[10**9] * n for _ in range(m)]
        dist[0][0] = 0
        hq = [(0, 0, 0)]
        while hq:
            cost, r, c = heapq.heappop(hq)
            if cost > dist[r][c]:
                continue
            if r == m - 1 and c == n - 1:
                return cost
            for i, (dr, dc) in enumerate(dirs):
                nr, nc = r + dr, c + dc
                if 0 <= nr < m and 0 <= nc < n:
                    ncost = cost + (0 if grid[r][c] == i + 1 else 1)
                    if ncost < dist[nr][nc]:
                        dist[nr][nc] = ncost
                        heapq.heappush(hq, (ncost, nr, nc))
        return dist[m - 1][n - 1]
# @lc code=end
