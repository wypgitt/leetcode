#
# @lc app=leetcode id=490 lang=python3
#
# [490] The Maze
#
# https://leetcode.com/problems/the-maze/description/
#
# algorithms
# Medium (60.49%)
# Likes:    1932
# Dislikes: 199
# Total Accepted:    211.9K
# Total Submissions: 350.2K
# Testcase Example:  "[[0,0,1,0,0],[0,0,0,0,0],[0,0,0,1,0],[1,1,0,1,1],[0,0,0,0,0]]\n[0,4]\n[4,4]"
#
#
# There is a ball in a maze with empty spaces (represented as 0) and walls
# (represented as 1). The ball can go through the empty spaces by rolling
# up, down, left or right, but it won't stop rolling until hitting a wall.
# When the ball stops, it could choose the next direction.
#
# Given the m x n maze, the ball's start position and the destination,
# where start = [start_row, start_col] and destination = [destination_row,
# destination_col], return true if the ball can stop at the destination,
# otherwise return false.
#
# You may assume that the borders of the maze are all walls (see
# examples).
#
# Example 1:
#
# Input: maze =
# [[0,0,1,0,0],[0,0,0,0,0],[0,0,0,1,0],[1,1,0,1,1],[0,0,0,0,0]], start =
# [0,4], destination = [4,4]
# Output: true
# Explanation: One possible way is : left -> down -> left -> down -> right
# -> down -> right.
#
# Example 2:
#
# Input: maze =
# [[0,0,1,0,0],[0,0,0,0,0],[0,0,0,1,0],[1,1,0,1,1],[0,0,0,0,0]], start =
# [0,4], destination = [3,2]
# Output: false
# Explanation: There is no way for the ball to stop at the destination.
# Notice that you can pass through the destination but you cannot stop
# there.
#
# Example 3:
#
# Input: maze =
# [[0,0,0,0,0],[1,1,0,0,1],[0,0,0,0,0],[0,1,0,0,1],[0,1,0,0,0]], start =
# [4,3], destination = [0,1]
# Output: false
#
# Constraints:
#
# m == maze.length
#
# n == maze[i].length
#
# 1 <= m, n <= 100
#
# maze[i][j] is 0 or 1.
#
# start.length == 2
#
# destination.length == 2
#
# 0 <= start_row, destination_row < m
#
# 0 <= start_col, destination_col < n
#
# Both the ball and the destination exist in an empty space, and they will
# not be in the same position initially.
#
# The maze contains at least 2 empty spaces.
#
# @lc code=start
from collections import deque
from typing import List


class Solution:
    def hasPath(
        self, maze: List[List[int]], start: List[int], destination: List[int]
    ) -> bool:
        """
        Interview explanation:
        Premium. Ball rolls until hitting a wall. BFS/DFS on stop positions
        (not every cell): from each stop, roll in 4 directions to the next
        stop; success if destination is reached as a stop.

        Algorithm (BFS):
        - Queue start; visited stop cells.
        - For each dir, roll while next cell empty; enqueue stop if new.
        - Return True if stop == destination.

        Complexity: O(mn * max(m,n)) time, O(mn) space.
        """
        m, n = len(maze), len(maze[0])
        dest = (destination[0], destination[1])
        q = deque([(start[0], start[1])])
        seen = {(start[0], start[1])}
        dirs = [(-1, 0), (1, 0), (0, -1), (0, 1)]

        while q:
            r, c = q.popleft()
            if (r, c) == dest:
                return True
            for dr, dc in dirs:
                nr, nc = r, c
                while (
                    0 <= nr + dr < m
                    and 0 <= nc + dc < n
                    and maze[nr + dr][nc + dc] == 0
                ):
                    nr += dr
                    nc += dc
                if (nr, nc) not in seen:
                    seen.add((nr, nc))
                    q.append((nr, nc))
        return False

    def hasPath_dfs(
        self, maze: List[List[int]], start: List[int], destination: List[int]
    ) -> bool:
        """
        Interview explanation:
        Alternate classic: DFS on stop positions with the same roll logic.

        Complexity: O(mn * max(m,n)) time, O(mn) space.
        """
        m, n = len(maze), len(maze[0])
        dest = (destination[0], destination[1])
        seen = set()
        dirs = [(-1, 0), (1, 0), (0, -1), (0, 1)]

        def dfs(r: int, c: int) -> bool:
            if (r, c) == dest:
                return True
            if (r, c) in seen:
                return False
            seen.add((r, c))
            for dr, dc in dirs:
                nr, nc = r, c
                while (
                    0 <= nr + dr < m
                    and 0 <= nc + dc < n
                    and maze[nr + dr][nc + dc] == 0
                ):
                    nr += dr
                    nc += dc
                if dfs(nr, nc):
                    return True
            return False

        return dfs(start[0], start[1])
# @lc code=end
