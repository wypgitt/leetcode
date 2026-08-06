#
# @lc app=leetcode id=1102 lang=python3
#
# [1102] Path With Maximum Minimum Value
#
# https://leetcode.com/problems/path-with-maximum-minimum-value/description/
#
# algorithms
# Medium (54.75%)
# Likes:    1359
# Dislikes: 126
# Total Accepted:    73.4K
# Total Submissions: 134K
# Testcase Example:  "[[5,4,5],[1,2,6],[7,4,6]]"
#
#
# Given an m x n integer matrix grid, return the maximum score of a path
# starting at (0, 0) and ending at (m - 1, n - 1) moving in the 4 cardinal
# directions.
#
# The score of a path is the minimum value in that path.
#
# For example, the score of the path 8 → 4 → 5 → 9 is 4.
#
# Example 1:
#
# Input: grid = [[5,4,5],[1,2,6],[7,4,6]]
# Output: 4
# Explanation: The path with the maximum score is highlighted in yellow.
#
# Example 2:
#
# Input: grid = [[2,2,1,2,2,2],[1,2,2,2,1,2]]
# Output: 2
#
# Example 3:
#
# Input: grid =
# [[3,4,6,3,4],[0,2,1,1,7],[8,8,3,2,7],[3,2,4,9,8],[4,1,2,0,0],[4,6,5,4,3]]
# Output: 3
#
# Constraints:
#
# m == grid.length
#
# n == grid[i].length
#
# 1 <= m, n <= 100
#
# 0 <= grid[i][j] <= 10^9
#
# @lc code=start
from typing import List
from collections import deque
import heapq


class Solution:
    def maximumMinimumPath(self, grid: List[List[int]]) -> int:
        """
        Interview explanation:
        Premium. Maximize the minimum value along a 4-connected path from
        (0,0) to (m-1,n-1). Binary search the score; for each mid, BFS/DFS
        only through cells ≥ mid.

        Algorithm (binary search + BFS):
        - lo=0, hi=min(grid[0][0], grid[-1][-1]).
        - feasible(x): BFS cells with value≥x.
        - Maximize x with feasible(x).

        Complexity: O(mn log V) time, O(mn) space.
        """
        m, n = len(grid), len(grid[0])
        dirs = [(0, 1), (1, 0), (0, -1), (-1, 0)]

        def feasible(x: int) -> bool:
            if grid[0][0] < x:
                return False
            seen = [[False] * n for _ in range(m)]
            q = deque([(0, 0)])
            seen[0][0] = True
            while q:
                r, c = q.popleft()
                if r == m - 1 and c == n - 1:
                    return True
                for dr, dc in dirs:
                    nr, nc = r + dr, c + dc
                    if 0 <= nr < m and 0 <= nc < n and not seen[nr][nc] and grid[nr][nc] >= x:
                        seen[nr][nc] = True
                        q.append((nr, nc))
            return False

        lo, hi = 0, min(grid[0][0], grid[m - 1][n - 1])
        ans = 0
        while lo <= hi:
            mid = (lo + hi) // 2
            if feasible(mid):
                ans = mid
                lo = mid + 1
            else:
                hi = mid - 1
        return ans

    def maximumMinimumPath_dijkstra(self, grid: List[List[int]]) -> int:
        """
        Interview explanation:
        Alternate: modified Dijkstra / best-first — always expand the cell
        that maximizes the path-min so far (max-heap of (min_so_far, r, c)).

        Algorithm (Dijkstra-style):
        - Push (-grid[0][0], 0, 0); visited.
        - Pop best; at end return score; push neighbors with min(score, cell).

        Complexity: O(mn log(mn)) time, O(mn) space.
        """
        m, n = len(grid), len(grid[0])
        dirs = [(0, 1), (1, 0), (0, -1), (-1, 0)]
        seen = [[False] * n for _ in range(m)]
        heap = [(-grid[0][0], 0, 0)]
        seen[0][0] = True
        while heap:
            score, r, c = heapq.heappop(heap)
            score = -score
            if r == m - 1 and c == n - 1:
                return score
            for dr, dc in dirs:
                nr, nc = r + dr, c + dc
                if 0 <= nr < m and 0 <= nc < n and not seen[nr][nc]:
                    seen[nr][nc] = True
                    heapq.heappush(heap, (-min(score, grid[nr][nc]), nr, nc))
        return 0
# @lc code=end
