#
# @lc app=leetcode id=2258 lang=python3
#
# [2258] Escape the Spreading Fire
#
# https://leetcode.com/problems/escape-the-spreading-fire/description/
#
# algorithms
# Hard (38.95%)
# Likes:    910
# Dislikes: 43
# Total Accepted:    22.8K
# Total Submissions: 58.6K
# Testcase Example:  "[[0,2,0,0,0,0,0],[0,0,0,2,2,1,0],[0,2,0,0,1,2,0],[0,0,2,2,2,0,2],[0,0,0,0,0,0,0]]"
#
# You are given a 0-indexed 2D integer array grid of size m x n which represents
# a field. Each cell has one of three values:
#
#
# 0 represents grass,
#
#
# 1 represents fire,
#
#
# 2 represents a wall that you and fire cannot pass through.
#
# You are situated in the top-left cell, (0, 0), and you want to travel to the
# safehouse at the bottom-right cell, (m - 1, n - 1). Every minute, you may move
# to an adjacent grass cell. After your move, every fire cell will spread to all
# adjacent cells that are not walls.
#
# Return the maximum number of minutes that you can stay in your initial
# position before moving while still safely reaching the safehouse. If this is
# impossible, return -1. If you can always reach the safehouse regardless of the
# minutes stayed, return 10^9.
#
# Note that even if the fire spreads to the safehouse immediately after you have
# reached it, it will be counted as safely reaching the safehouse.
#
# A cell is adjacent to another cell if the former is directly north, east,
# south, or west of the latter (i.e., their sides are touching).
#
#
#
# Example 1:
#
# Input: grid =
# [[0,2,0,0,0,0,0],[0,0,0,2,2,1,0],[0,2,0,0,1,2,0],[0,0,2,2,2,0,2],[0,0,0,0,0,0,0]]
# Output: 3
# Explanation: The figure above shows the scenario where you stay in the initial
# position for 3 minutes.
# You will still be able to safely reach the safehouse.
# Staying for more than 3 minutes will not allow you to safely reach the
# safehouse.
#
# Example 2:
#
# Input: grid = [[0,0,0,0],[0,1,2,0],[0,2,0,0]]
# Output: -1
# Explanation: The figure above shows the scenario where you immediately move
# towards the safehouse.
# Fire will spread to any cell you move towards and it is impossible to safely
# reach the safehouse.
# Thus, -1 is returned.
#
# Example 3:
#
# Input: grid = [[0,0,0],[2,2,0],[1,2,0]]
# Output: 1000000000
# Explanation: The figure above shows the initial grid.
# Notice that the fire is contained by walls and you will always be able to
# safely reach the safehouse.
# Thus, 10^9 is returned.
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
# 2 <= m, n <= 300
#
#
# 4 <= m * n <= 2 * 10^4
#
#
# grid[i][j] is either 0, 1, or 2.
#
#
# grid[0][0] == grid[m - 1][n - 1] == 0
#

# @lc code=start
from typing import List
from collections import deque
from itertools import pairwise


class Solution:
    def maximumMinutes(self, grid: List[List[int]]) -> int:
        """
        Interview explanation:
        Stay at (0,0) for t minutes, then move 4-dir to (m-1,n-1). Each minute
        you move first, then fire spreads to adjacent grass. Maximize t; -1 if
        impossible; 10^9 if unbounded.

        Algorithm:
        - Binary search t in [-1, m*n]. Feasibility: spread fire for t minutes,
          then BFS person moves interleaved with fire spread rounds; may enter
          safehouse even as fire arrives there next.

        Complexity: O(mn log(mn)) time, O(mn) space.
        """
        m, n = len(grid), len(grid[0])
        dirs = (-1, 0, 1, 0, -1)
        fire = [[False] * n for _ in range(m)]

        def spread(q: deque) -> deque:
            nq = deque()
            while q:
                i, j = q.popleft()
                for a, b in pairwise(dirs):
                    x, y = i + a, j + b
                    if 0 <= x < m and 0 <= y < n and not fire[x][y] and grid[x][y] == 0:
                        fire[x][y] = True
                        nq.append((x, y))
            return nq

        def check(t: int) -> bool:
            for i in range(m):
                for j in range(n):
                    fire[i][j] = False
            q1 = deque()
            for i in range(m):
                for j in range(n):
                    if grid[i][j] == 1:
                        fire[i][j] = True
                        q1.append((i, j))
            while t and q1:
                q1 = spread(q1)
                t -= 1
            if fire[0][0]:
                return False
            q2 = deque([(0, 0)])
            vis = [[False] * n for _ in range(m)]
            vis[0][0] = True
            while q2:
                for _ in range(len(q2)):
                    i, j = q2.popleft()
                    if fire[i][j]:
                        continue
                    for a, b in pairwise(dirs):
                        x, y = i + a, j + b
                        if (
                            0 <= x < m
                            and 0 <= y < n
                            and not vis[x][y]
                            and not fire[x][y]
                            and grid[x][y] == 0
                        ):
                            if x == m - 1 and y == n - 1:
                                return True
                            vis[x][y] = True
                            q2.append((x, y))
                q1 = spread(q1)
            return False

        lo, hi = -1, m * n
        while lo < hi:
            mid = (lo + hi + 1) // 2
            if check(mid):
                lo = mid
            else:
                hi = mid - 1
        return 10**9 if lo == m * n else lo
# @lc code=end
