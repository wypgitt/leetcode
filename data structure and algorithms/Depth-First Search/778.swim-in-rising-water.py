#
# @lc app=leetcode id=778 lang=python3
#
# [778] Swim in Rising Water
#
# https://leetcode.com/problems/swim-in-rising-water/description/
#
# algorithms
# Hard (68.13%)
# Likes:    4680
# Dislikes: 320
# Total Accepted:    406K
# Total Submissions: 596K
# Testcase Example:  "[[0,2],[1,3]]"
#
# You are given an n x n integer matrix grid where each value grid[i][j]
# represents the elevation at that point (i, j).
#
# It starts raining, and water gradually rises over time. At time t, the water
# level is t, meaning any cell with elevation less than equal to t is submerged
# or reachable.
#
# You can swim from a square to another 4-directionally adjacent square if and
# only if the elevation of both squares individually are at most t. You can
# swim infinite distances in zero time. Of course, you must stay within the
# boundaries of the grid during your swim.
#
# Return the minimum time until you can reach the bottom right square (n - 1, n
# - 1) if you start at the top left square (0, 0).
#
# Example 1:
#
# Input: grid = [[0,2],[1,3]]
# Output: 3
# Explanation:
# At time 0, you are in grid location (0, 0).
# You cannot go anywhere else because 4-directionally adjacent neighbors have a
# higher elevation than t = 0.
# You cannot reach point (1, 1) until time 3.
# When the depth of water is 3, we can swim anywhere inside the grid.
#
# Example 2:
#
# Input: grid =
# [[0,1,2,3,4],[24,23,22,21,5],[12,13,14,15,16],[11,17,18,19,20],[10,9,8,7,6]]
# Output: 16
# Explanation: The final route is shown.
# We need to wait until time 16 so that (0, 0) and (4, 4) are connected.
#
# Constraints:
#
# n == grid.length
#
# n == grid[i].length
#
# 1 <= n <= 50
#
# 0 <= grid[i][j] < n^2
#
# Each value grid[i][j] is unique.
#

# @lc code=start
import heapq
from collections import deque
from typing import List


class Solution:
    def swimInWater(self, grid: List[List[int]]) -> int:
        """
        Interview explanation:
        Wait until time t = max elevation on the path; find path minimizing that
        max. Dijkstra on cells with cost = max(elevation so far, cell height)
        is the classic best solution (also binary-search + BFS / Union-Find).

        Algorithm (Dijkstra):
        - Min-heap of (time, r, c); time = max elevation needed to reach cell.
        - Pop smallest time; if (n-1,n-1) return it. Push unvisited neighbors
          with max(time, grid[nr][nc]).

        Complexity: O(n^2 log n) time, O(n^2) space.
        """
        n = len(grid)
        seen = [[False] * n for _ in range(n)]
        heap = [(grid[0][0], 0, 0)]
        seen[0][0] = True
        while heap:
            t, r, c = heapq.heappop(heap)
            if r == n - 1 and c == n - 1:
                return t
            for nr, nc in ((r - 1, c), (r + 1, c), (r, c - 1), (r, c + 1)):
                if 0 <= nr < n and 0 <= nc < n and not seen[nr][nc]:
                    seen[nr][nc] = True
                    heapq.heappush(heap, (max(t, grid[nr][nc]), nr, nc))
        return -1

    def swimInWater_binary_search_bfs(self, grid: List[List[int]]) -> int:
        """
        Interview explanation:
        Alternate classic: binary search t; BFS/DFS whether (0,0) reaches
        (n-1,n-1) using only cells with height <= t (and t >= grid[0][0]).

        Algorithm:
        - lo = grid[0][0], hi = n*n-1 (or max grid).
        - can(t): BFS over cells <= t.
        - Minimize t with can(t).

        Complexity: O(n^2 log (n^2)) time, O(n^2) space.
        """
        n = len(grid)

        def can(t: int) -> bool:
            if grid[0][0] > t:
                return False
            q = deque([(0, 0)])
            seen = {(0, 0)}
            while q:
                r, c = q.popleft()
                if r == n - 1 and c == n - 1:
                    return True
                for nr, nc in ((r - 1, c), (r + 1, c), (r, c - 1), (r, c + 1)):
                    if 0 <= nr < n and 0 <= nc < n and (nr, nc) not in seen and grid[nr][nc] <= t:
                        seen.add((nr, nc))
                        q.append((nr, nc))
            return False

        lo, hi = grid[0][0], n * n - 1
        while lo < hi:
            mid = (lo + hi) // 2
            if can(mid):
                hi = mid
            else:
                lo = mid + 1
        return lo

    def swimInWater_union_find(self, grid: List[List[int]]) -> int:
        """
        Interview explanation:
        Alternate: sort cells by height ascending; Union-Find adjacent cells
        already "unlocked". First time (0,0) connects to (n-1,n-1), answer =
        that cell's height.

        Algorithm:
        - Sort (height,r,c); activate cells in order; union with active neighbors.
        - When find(0)==find(n*n-1), return height.

        Complexity: O(n^2 log n) time (sort), O(n^2) space.
        """
        n = len(grid)
        parent = list(range(n * n))

        def find(x: int) -> int:
            while parent[x] != x:
                parent[x] = parent[parent[x]]
                x = parent[x]
            return x

        def union(a: int, b: int) -> None:
            ra, rb = find(a), find(b)
            if ra != rb:
                parent[rb] = ra

        order = sorted(((grid[i][j], i, j) for i in range(n) for j in range(n)))
        active = [[False] * n for _ in range(n)]
        for h, r, c in order:
            active[r][c] = True
            idx = r * n + c
            for nr, nc in ((r - 1, c), (r + 1, c), (r, c - 1), (r, c + 1)):
                if 0 <= nr < n and 0 <= nc < n and active[nr][nc]:
                    union(idx, nr * n + nc)
            if find(0) == find(n * n - 1):
                return h
        return -1
# @lc code=end

