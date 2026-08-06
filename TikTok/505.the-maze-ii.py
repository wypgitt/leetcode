#
# @lc app=leetcode id=505 lang=python3
#
# [505] The Maze II
#
# https://leetcode.com/problems/the-maze-ii/description/
#
# algorithms
# Medium (55.18%)
# Likes:    1405
# Dislikes: 64
# Total Accepted:    130.5K
# Total Submissions: 236.6K
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
# destination_col], return the shortest distance for the ball to stop at
# the destination. If the ball cannot stop at destination, return -1.
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
# [[0,0,1,0,0],[0,0,0,0,0],[0,0,0,1,0],[1,1,0,1,1],[0,0,0,0,0]], start =
# [0,4], destination = [4,4]
# Output: 12
# Explanation: One possible way is : left -> down -> left -> down -> right
# -> down -> right.
# The length of the path is 1 + 1 + 3 + 1 + 2 + 2 + 2 = 12.
#
# Example 2:
#
# Input: maze =
# [[0,0,1,0,0],[0,0,0,0,0],[0,0,0,1,0],[1,1,0,1,1],[0,0,0,0,0]], start =
# [0,4], destination = [3,2]
# Output: -1
# Explanation: There is no way for the ball to stop at the destination.
# Notice that you can pass through the destination but you cannot stop
# there.
#
# Example 3:
#
# Input: maze =
# [[0,0,0,0,0],[1,1,0,0,1],[0,0,0,0,0],[0,1,0,0,1],[0,1,0,0,0]], start =
# [4,3], destination = [0,1]
# Output: -1
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
import heapq
from collections import deque
from typing import List


class Solution:
    def shortestDistance(
        self, maze: List[List[int]], start: List[int], destination: List[int]
    ) -> int:
        """
        Interview explanation:
        Premium. Shortest rolled distance to destination stop. Dijkstra (or 0-1
        BFS variant) on stop positions: edge weight = cells rolled.

        Algorithm (Dijkstra):
        - dist[start]=0; min-heap (d,r,c).
        - Pop; roll 4 dirs to next stop with steps; relax dist[stop].
        - Return dist[dest] or -1.

        Complexity: O(mn * max(m,n) * log(mn)) time, O(mn) space.
        """
        m, n = len(maze), len(maze[0])
        dest = (destination[0], destination[1])
        dist = {(start[0], start[1]): 0}
        heap = [(0, start[0], start[1])]
        dirs = [(-1, 0), (1, 0), (0, -1), (0, 1)]

        while heap:
            d, r, c = heapq.heappop(heap)
            if (r, c) == dest:
                return d
            if d > dist.get((r, c), float("inf")):
                continue
            for dr, dc in dirs:
                nr, nc, steps = r, c, 0
                while (
                    0 <= nr + dr < m
                    and 0 <= nc + dc < n
                    and maze[nr + dr][nc + dc] == 0
                ):
                    nr += dr
                    nc += dc
                    steps += 1
                nd = d + steps
                if nd < dist.get((nr, nc), float("inf")):
                    dist[(nr, nc)] = nd
                    heapq.heappush(heap, (nd, nr, nc))
        return -1

    def shortestDistance_bfs(
        self, maze: List[List[int]], start: List[int], destination: List[int]
    ) -> int:
        """
        Interview explanation:
        Alternate: BFS over stops while tracking best distance (like Dijkstra
        without heap when using a dist array and only enqueue on improvement).

        Complexity: O(mn * max(m,n)) time, O(mn) space.
        """
        m, n = len(maze), len(maze[0])
        dest = (destination[0], destination[1])
        dist = [[float("inf")] * n for _ in range(m)]
        dist[start[0]][start[1]] = 0
        q = deque([(start[0], start[1])])
        dirs = [(-1, 0), (1, 0), (0, -1), (0, 1)]
        while q:
            r, c = q.popleft()
            for dr, dc in dirs:
                nr, nc, steps = r, c, 0
                while (
                    0 <= nr + dr < m
                    and 0 <= nc + dc < n
                    and maze[nr + dr][nc + dc] == 0
                ):
                    nr += dr
                    nc += dc
                    steps += 1
                if dist[r][c] + steps < dist[nr][nc]:
                    dist[nr][nc] = dist[r][c] + steps
                    q.append((nr, nc))
        ans = dist[dest[0]][dest[1]]
        return int(ans) if ans < float("inf") else -1
# @lc code=end
