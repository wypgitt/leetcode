#
# @lc app=leetcode id=3286 lang=python3
#
# [3286] Find a Safe Walk Through a Grid
#
# https://leetcode.com/problems/find-a-safe-walk-through-a-grid/description/
#
# algorithms
# Medium (55.47%)
# Likes:    540
# Dislikes: 22
# Total Accepted:    136.2K
# Total Submissions: 245.5K
# Testcase Example:  "[[0,1,0,0,0],[0,1,0,1,0],[0,0,0,1,0]]\n1"
#
#
# You are given an m x n binary matrix grid and an integer health.
#
# You start on the upper-left corner (0, 0) and would like to get to the
# lower-right corner (m - 1, n - 1).
#
# You can move up, down, left, or right from one cell to another adjacent
# cell as long as your health remains positive.
#
# Cells (i, j) with grid[i][j] = 1 are considered unsafe and reduce your
# health by 1.
#
# Return true if you can reach the final cell with a health value of 1 or
# more, and false otherwise.
#
# Example 1:
#
# Input: grid = [[0,1,0,0,0],[0,1,0,1,0],[0,0,0,1,0]], health = 1
#
# Output: true
#
# Explanation:
#
# The final cell can be reached safely by walking along the gray cells
# below.
#
# Example 2:
#
# Input: grid = [[0,1,1,0,0,0],[1,0,1,0,0,0],[0,1,1,1,0,1],[0,0,1,0,1,0]],
# health = 3
#
# Output: false
#
# Explanation:
#
# A minimum of 4 health points is needed to reach the final cell safely.
#
# Example 3:
#
# Input: grid = [[1,1,1],[1,0,1],[1,1,1]], health = 5
#
# Output: true
#
# Explanation:
#
# The final cell can be reached safely by walking along the gray cells
# below.
#
# Any path that does not go through the cell (1, 1) is unsafe since your
# health will drop to 0 when reaching the final cell.
#
# Constraints:
#
# m == grid.length
#
# n == grid[i].length
#
# 1 <= m, n <= 50
#
# 2 <= m * n
#
# 1 <= health <= m + n
#
# grid[i][j] is either 0 or 1.
#

# @lc code=start
from collections import deque
from typing import List


class Solution:
    def findSafeWalk(self, grid: List[List[int]], health: int) -> bool:
        """
        Interview explanation:
        Reach (m-1,n-1) with health >= 1; unsafe cells cost 1 health. Minimize
        damage (0-1 BFS) and compare against the budget.

        Algorithm:
        - 0-1 BFS / deque: cost 0 on safe cells, 1 on unsafe; start pays grid[0][0].
        - Succeed if min damage to the end <= health - 1.
        - Alternate: BFS on state (r,c,health_left).

        Complexity: O(mn) time, O(mn) space.
        """
        m, n = len(grid), len(grid[0])
        dist = [[10**9] * n for _ in range(m)]
        dist[0][0] = grid[0][0]
        q = deque([(0, 0)])
        while q:
            r, c = q.popleft()
            for nr, nc in ((r - 1, c), (r + 1, c), (r, c - 1), (r, c + 1)):
                if 0 <= nr < m and 0 <= nc < n:
                    nd = dist[r][c] + grid[nr][nc]
                    if nd < dist[nr][nc]:
                        dist[nr][nc] = nd
                        if grid[nr][nc] == 0:
                            q.appendleft((nr, nc))
                        else:
                            q.append((nr, nc))
        return dist[m - 1][n - 1] <= health - 1
# @lc code=end
