#
# @lc app=leetcode id=2812 lang=python3
#
# [2812] Find the Safest Path in a Grid
#
# https://leetcode.com/problems/find-the-safest-path-in-a-grid/description/
#
# algorithms
# Medium (57.32%)
# Likes:    2282
# Dislikes: 355
# Total Accepted:    205.1K
# Total Submissions: 357.9K
# Testcase Example:  "[[1,0,0],[0,0,0],[0,0,1]]"
#
#
# You are given a 0-indexed 2D matrix grid of size n x n, where (r, c)
# represents:
#
# A cell containing a thief if grid[r][c] = 1
#
# An empty cell if grid[r][c] = 0
#
# You are initially positioned at cell (0, 0). In one move, you can move
# to any adjacent cell in the grid, including cells containing thieves.
#
# The safeness factor of a path on the grid is defined as the minimum
# manhattan distance from any cell in the path to any thief in the grid.
#
# Return the maximum safeness factor of all paths leading to cell (n - 1,
# n - 1).
#
# An adjacent cell of cell (r, c), is one of the cells (r, c + 1), (r, c -
# 1), (r + 1, c) and (r - 1, c) if it exists.
#
# The Manhattan distance between two cells (a, b) and (x, y) is equal to
# |a - x| + |b - y|, where |val| denotes the absolute value of val.
#
# Example 1:
#
# Input: grid = [[1,0,0],[0,0,0],[0,0,1]]
# Output: 0
# Explanation: All paths from (0, 0) to (n - 1, n - 1) go through the
# thieves in cells (0, 0) and (n - 1, n - 1).
#
# Example 2:
#
# Input: grid = [[0,0,1],[0,0,0],[0,0,0]]
# Output: 2
# Explanation: The path depicted in the picture above has a safeness
# factor of 2 since:
# - The closest cell of the path to the thief at cell (0, 2) is cell (0,
# 0). The distance between them is | 0 - 0 | + | 0 - 2 | = 2.
# It can be shown that there are no other paths with a higher safeness
# factor.
#
# Example 3:
#
# Input: grid = [[0,0,0,1],[0,0,0,0],[0,0,0,0],[1,0,0,0]]
# Output: 2
# Explanation: The path depicted in the picture above has a safeness
# factor of 2 since:
# - The closest cell of the path to the thief at cell (0, 3) is cell (1,
# 2). The distance between them is | 0 - 1 | + | 3 - 2 | = 2.
# - The closest cell of the path to the thief at cell (3, 0) is cell (3,
# 2). The distance between them is | 3 - 3 | + | 0 - 2 | = 2.
# It can be shown that there are no other paths with a higher safeness
# factor.
#
# Constraints:
#
# 1 <= grid.length == n <= 400
#
# grid[i].length == n
#
# grid[i][j] is either 0 or 1.
#
# There is at least one thief in the grid.
#

# @lc code=start
from collections import deque
from typing import List


class Solution:
    def maximumSafenessFactor(self, grid: List[List[int]]) -> int:
        """
        Interview explanation:
        Safeness of a path is the min Manhattan distance from any cell on the
        path to a thief (1). Maximize safeness of a path from (0,0) to (n-1,n-1).

        Algorithm:
        - Multi-source BFS from all thieves -> dist[r][c] to nearest thief.
        - Binary search safeness sf; BFS/check path using only cells with
          dist >= sf (start/end must also satisfy).

        Complexity: O(n^2 log n) time, O(n^2) space.
        """
        n = len(grid)
        dist = [[-1] * n for _ in range(n)]
        q: deque = deque()
        for i in range(n):
            for j in range(n):
                if grid[i][j] == 1:
                    dist[i][j] = 0
                    q.append((i, j))
        dirs = ((1, 0), (-1, 0), (0, 1), (0, -1))
        while q:
            r, c = q.popleft()
            for dr, dc in dirs:
                nr, nc = r + dr, c + dc
                if 0 <= nr < n and 0 <= nc < n and dist[nr][nc] == -1:
                    dist[nr][nc] = dist[r][c] + 1
                    q.append((nr, nc))

        def ok(sf: int) -> bool:
            if dist[0][0] < sf or dist[n - 1][n - 1] < sf:
                return False
            seen = [[False] * n for _ in range(n)]
            dq: deque = deque([(0, 0)])
            seen[0][0] = True
            while dq:
                r, c = dq.popleft()
                if (r, c) == (n - 1, n - 1):
                    return True
                for dr, dc in dirs:
                    nr, nc = r + dr, c + dc
                    if (
                        0 <= nr < n
                        and 0 <= nc < n
                        and not seen[nr][nc]
                        and dist[nr][nc] >= sf
                    ):
                        seen[nr][nc] = True
                        dq.append((nr, nc))
            return False

        lo, hi = 0, n * 2
        while lo < hi:
            mid = (lo + hi + 1) // 2
            if ok(mid):
                lo = mid
            else:
                hi = mid - 1
        return lo
# @lc code=end
