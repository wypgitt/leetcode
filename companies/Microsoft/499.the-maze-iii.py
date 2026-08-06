#
# @lc app=leetcode id=499 lang=python3
#
# [499] The Maze III
#
# https://leetcode.com/problems/the-maze-iii/description/
#
# algorithms
# Hard (52.58%)
# Likes:    525
# Dislikes: 78
# Total Accepted:    41.2K
# Total Submissions: 78.3K
# Testcase Example:  "[[0,0,0,0,0],[1,1,0,0,1],[0,0,0,0,0],[0,1,0,0,1],[0,1,0,0,0]]\n[4,3]\n[0,1]"
#
#
# There is a ball in a maze with empty spaces (represented as 0) and walls
# (represented as 1). The ball can go through the empty spaces by rolling
# up, down, left or right, but it won't stop rolling until hitting a wall.
# When the ball stops, it could choose the next direction (must be
# different from last chosen direction). There is also a hole in this
# maze. The ball will drop into the hole if it rolls onto the hole.
#
# Given the m x n maze, the ball's position ball and the hole's position
# hole, where ball = [ball_row, ball_col] and hole = [hole_row, hole_col],
# return a string instructions of all the instructions that the ball
# should follow to drop in the hole with the shortest distance possible.
# If there are multiple valid instructions, return the lexicographically
# minimum one. If the ball can't drop in the hole, return "impossible".
#
# If there is a way for the ball to drop in the hole, the answer
# instructions should contain the characters 'u' (i.e., up), 'd' (i.e.,
# down), 'l' (i.e., left), and 'r' (i.e., right).
#
# The distance is the number of empty spaces traveled by the ball from the
# start position (excluded) to the destination (included).
#
# You may assume that the borders of the maze are all walls (see
# examples).
#
# Example 1:
#
# Input: maze =
# [[0,0,0,0,0],[1,1,0,0,1],[0,0,0,0,0],[0,1,0,0,1],[0,1,0,0,0]], ball =
# [4,3], hole = [0,1]
# Output: "lul"
# Explanation: There are two shortest ways for the ball to drop into the
# hole.
# The first way is left -> up -> left, represented by "lul".
# The second way is up -> left, represented by 'ul'.
# Both ways have shortest distance 6, but the first way is
# lexicographically smaller because 'l' < 'u'. So the output is "lul".
#
# Example 2:
#
# Input: maze =
# [[0,0,0,0,0],[1,1,0,0,1],[0,0,0,0,0],[0,1,0,0,1],[0,1,0,0,0]], ball =
# [4,3], hole = [3,0]
# Output: "impossible"
# Explanation: The ball cannot reach the hole.
#
# Example 3:
#
# Input: maze =
# [[0,0,0,0,0,0,0],[0,0,1,0,0,1,0],[0,0,0,0,1,0,0],[0,0,0,0,0,0,1]], ball
# = [0,4], hole = [3,5]
# Output: "dldr"
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
# ball.length == 2
#
# hole.length == 2
#
# 0 <= ball_row, hole_row <= m
#
# 0 <= ball_col, hole_col <= n
#
# Both the ball and the hole exist in an empty space, and they will not be
# in the same position initially.
#
# The maze contains at least 2 empty spaces.
#
# @lc code=start
import heapq
from typing import List


class Solution:
    def findShortestWay(
        self, maze: List[List[int]], ball: List[int], hole: List[int]
    ) -> str:
        """
        Interview explanation:
        Premium. Dijkstra on stop positions: minimize distance, then
        lexicographically smallest path string among ties. Rolling stops when
        hitting a wall or falling into the hole.

        Algorithm:
        - Min-heap (dist, path, r, c); dist_map best (dist, path) per cell.
        - From each stop, roll in dirs d/l/r/u (lex order of instruction names
          handled by comparing path strings); stop at wall or hole.
        - Return path at hole or "impossible".

        Complexity: O(mn * max(m,n) * log(mn)) time, O(mn) space.
        """
        m, n = len(maze), len(maze[0])
        hole_t = (hole[0], hole[1])
        # directions in any order; path string comparison handles lex order
        dirs = [("u", -1, 0), ("d", 1, 0), ("l", 0, -1), ("r", 0, 1)]
        best = {}
        heap = [(0, "", ball[0], ball[1])]  # dist, path, r, c
        best[(ball[0], ball[1])] = (0, "")

        while heap:
            dist, path, r, c = heapq.heappop(heap)
            if (r, c) == hole_t:
                return path
            if best.get((r, c), (float("inf"), "")) < (dist, path):
                continue
            for ch, dr, dc in dirs:
                nr, nc, steps = r, c, 0
                while (
                    0 <= nr + dr < m
                    and 0 <= nc + dc < n
                    and maze[nr + dr][nc + dc] == 0
                ):
                    nr += dr
                    nc += dc
                    steps += 1
                    if (nr, nc) == hole_t:
                        break
                nd = dist + steps
                np = path + ch
                key = (nr, nc)
                if key not in best or (nd, np) < best[key]:
                    best[key] = (nd, np)
                    heapq.heappush(heap, (nd, np, nr, nc))
        return "impossible"
# @lc code=end
