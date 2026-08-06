#
# @lc app=leetcode id=1730 lang=python3
#
# [1730] Shortest Path to Get Food
#
# https://leetcode.com/problems/shortest-path-to-get-food/description/
#
# algorithms
# Medium (57.26%)
# Likes:    725
# Dislikes: 41
# Total Accepted:    83.9K
# Total Submissions: 146.5K
# Testcase Example:  "[[\"X\",\"X\",\"X\",\"X\",\"X\",\"X\"],[\"X\",\"*\",\"O\",\"O\",\"O\",\"X\"],[\"X\",\"O\",\"O\",\"#\",\"O\",\"X\"],[\"X\",\"X\",\"X\",\"X\",\"X\",\"X\"]]"
#
#
# You are starving and you want to eat food as quickly as possible. You
# want to find the shortest path to arrive at any food cell.
#
# You are given an m x n character matrix, grid, of these different types
# of cells:
#
# '*' is your location. There is exactly one '*' cell.
#
# '#' is a food cell. There may be multiple food cells.
#
# 'O' is free space, and you can travel through these cells.
#
# 'X' is an obstacle, and you cannot travel through these cells.
#
# You can travel to any adjacent cell north, east, south, or west of your
# current location if there is not an obstacle.
#
# Return the length of the shortest path for you to reach any food cell.
# If there is no path for you to reach food, return -1.
#
# Example 1:
#
# Input: grid =
# [["X","X","X","X","X","X"],["X","*","O","O","O","X"],["X","O","O","#","O","X"],["X","X","X","X","X","X"]]
# Output: 3
# Explanation: It takes 3 steps to reach the food.
#
# Example 2:
#
# Input: grid =
# [["X","X","X","X","X"],["X","*","X","O","X"],["X","O","X","#","X"],["X","X","X","X","X"]]
# Output: -1
# Explanation: It is not possible to reach the food.
#
# Example 3:
#
# Input: grid =
# [["X","X","X","X","X","X","X","X"],["X","*","O","X","O","#","O","X"],["X","O","O","X","O","O","X","X"],["X","O","O","O","O","#","O","X"],["X","X","X","X","X","X","X","X"]]
# Output: 6
# Explanation: There can be multiple food cells. It only takes 6 steps to
# reach the bottom food.
#
# Example 4:
#
# Input: grid =
# [["X","X","X","X","X","X","X","X"],["X","*","O","X","O","#","O","X"],["X","O","O","X","O","O","X","X"],["X","O","O","O","O","#","O","X"],["O","O","O","O","O","O","O","O"]]
# Output: 5
#
# Constraints:
#
# m == grid.length
#
# n == grid[i].length
#
# 1 <= m, n <= 200
#
# grid[row][col] is '*', 'X', 'O', or '#'.
#
# The grid contains exactly one '*'.
#
# @lc code=start
from typing import List
from collections import deque


class Solution:
    def getFood(self, grid: List[List[str]]) -> int:
        """
        Interview explanation:
        Premium. Grid with start "*", food "#", open "O", blocked "X". Shortest
        path from start to any food is unweighted BFS.

        Algorithm:
        - Find "*"; BFS 4-dir through "O"/"#"; return steps on "#", else -1.

        Complexity: O(mn) time, O(mn) space.
        """
        m, n = len(grid), len(grid[0])
        q = deque()
        for i in range(m):
            for j in range(n):
                if grid[i][j] == "*":
                    q.append((i, j, 0))
                    break
            if q:
                break
        seen = [[False] * n for _ in range(m)]
        if q:
            seen[q[0][0]][q[0][1]] = True
        while q:
            r, c, d = q.popleft()
            for dr, dc in ((0, 1), (1, 0), (0, -1), (-1, 0)):
                nr, nc = r + dr, c + dc
                if 0 <= nr < m and 0 <= nc < n and not seen[nr][nc] and grid[nr][nc] != "X":
                    if grid[nr][nc] == "#":
                        return d + 1
                    seen[nr][nc] = True
                    q.append((nr, nc, d + 1))
        return -1
# @lc code=end
