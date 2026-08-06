#
# @lc app=leetcode id=1926 lang=python3
#
# [1926] Nearest Exit from Entrance in Maze
#
# https://leetcode.com/problems/nearest-exit-from-entrance-in-maze/description/
#
# algorithms
# Medium (48.96%)
# Likes:    2673
# Dislikes: 128
# Total Accepted:    296K
# Total Submissions: 605K
# Testcase Example:  "[[\"+\",\"+\",\".\",\"+\"],[\".\",\".\",\".\",\"+\"],[\"+\",\"+\",\"+\",\".\"]]"
#
# You are given an m x n matrix maze (0-indexed) with empty cells (represented
# as '.') and walls (represented as '+'). You are also given the entrance of
# the maze, where entrance = [entrance_row, entrance_col] denotes the row and
# column of the cell you are initially standing at.
#
# In one step, you can move one cell up, down, left, or right. You cannot step
# into a cell with a wall, and you cannot step outside the maze. Your goal is
# to find the nearest exit from the entrance. An exit is defined as an empty
# cell that is at the border of the maze. The entrance does not count as an
# exit.
#
# Return the number of steps in the shortest path from the entrance to the
# nearest exit, or -1 if no such path exists.
#
# Example 1:
#
# Input: maze = [["+","+",".","+"],[".",".",".","+"],["+","+","+","."]],
# entrance = [1,2]
# Output: 1
# Explanation: There are 3 exits in this maze at [1,0], [0,2], and [2,3].
# Initially, you are at the entrance cell [1,2].
# - You can reach [1,0] by moving 2 steps left.
# - You can reach [0,2] by moving 1 step up.
# It is impossible to reach [2,3] from the entrance.
# Thus, the nearest exit is [0,2], which is 1 step away.
#
# Example 2:
#
# Input: maze = [["+","+","+"],[".",".","."],["+","+","+"]], entrance = [1,0]
# Output: 2
# Explanation: There is 1 exit in this maze at [1,2].
# [1,0] does not count as an exit since it is the entrance cell.
# Initially, you are at the entrance cell [1,0].
# - You can reach [1,2] by moving 2 steps right.
# Thus, the nearest exit is [1,2], which is 2 steps away.
#
# Example 3:
#
# Input: maze = [[".","+"]], entrance = [0,0]
# Output: -1
# Explanation: There are no exits in this maze.
#
# Constraints:
#
# maze.length == m
#
# maze[i].length == n
#
# 1 <= m, n <= 100
#
# maze[i][j] is either '.' or '+'.
#
# entrance.length == 2
#
# 0 <= entrance_row < m
#
# 0 <= entrance_col < n
#
# entrance will always be an empty cell.
#

# @lc code=start
from typing import List
from collections import deque


class Solution:
    def nearestExit(self, maze: List[List[str]], entrance: List[int]) -> int:
        """
        Interview explanation:
        Shortest path from entrance to any border empty cell (not the entrance).
        Unweighted grid → BFS.

        Algorithm:
        - BFS from entrance through '.'; mark visited; on reaching border cell
          that is not entrance, return steps; else -1.

        Complexity: O(mn) time/space.
        """
        m, n = len(maze), len(maze[0])
        er, ec = entrance
        q = deque([(er, ec, 0)])
        maze[er][ec] = "+"
        while q:
            r, c, d = q.popleft()
            for dr, dc in ((0, 1), (1, 0), (0, -1), (-1, 0)):
                nr, nc = r + dr, c + dc
                if 0 <= nr < m and 0 <= nc < n and maze[nr][nc] == ".":
                    if nr == 0 or nr == m - 1 or nc == 0 or nc == n - 1:
                        return d + 1
                    maze[nr][nc] = "+"
                    q.append((nr, nc, d + 1))
        return -1
# @lc code=end
