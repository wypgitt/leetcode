#
# @lc app=leetcode id=286 lang=python3
#
# [286] Walls and Gates
#
# https://leetcode.com/problems/walls-and-gates/description/
#
# algorithms
# Medium (64.12%)
# Likes:    3340
# Dislikes: 73
# Total Accepted:    434.5K
# Total Submissions: 677.6K
# Testcase Example:  "[[2147483647,-1,0,2147483647],[2147483647,2147483647,2147483647,-1],[2147483647,-1,2147483647,-1],[0,-1,2147483647,2147483647]]"
#
#
# You are given an m x n grid rooms initialized with these three possible
# values.
#
# -1 A wall or an obstacle.
#
# 0 A gate.
#
# INF Infinity means an empty room. We use the value 2^31 - 1 = 2147483647
# to represent INF as you may assume that the distance to a gate is less
# than 2147483647.
#
# Fill each empty room with the distance to its nearest gate. If it is
# impossible to reach a gate, it should be filled with INF.
#
# Example 1:
#
# Input: rooms =
# [[2147483647,-1,0,2147483647],[2147483647,2147483647,2147483647,-1],[2147483647,-1,2147483647,-1],[0,-1,2147483647,2147483647]]
# Output: [[3,-1,0,1],[2,2,1,-1],[1,-1,2,-1],[0,-1,3,4]]
#
# Example 2:
#
# Input: rooms = [[-1]]
# Output: [[-1]]
#
# Constraints:
#
# m == rooms.length
#
# n == rooms[i].length
#
# 1 <= m, n <= 250
#
# rooms[i][j] is -1, 0, or 2^31 - 1.
#
# @lc code=start
from collections import deque
from typing import List


class Solution:
    def wallsAndGates(self, rooms: List[List[int]]) -> None:
        """
        Interview explanation:
        0 = gate, -1 = wall, INF = empty. Fill each empty room with distance to
        nearest gate. Multi-source BFS from all gates at once.

        Algorithm:
        - Enqueue every gate; BFS level by level.
        - For each empty neighbor, set distance = parent + 1 and enqueue.
        - Visited implicitly: only expand into INF cells.

        Complexity: O(mn) time and space.
        """
        if not rooms or not rooms[0]:
            return
        m, n = len(rooms), len(rooms[0])
        INF = 2147483647
        q = deque()
        for i in range(m):
            for j in range(n):
                if rooms[i][j] == 0:
                    q.append((i, j))

        while q:
            r, c = q.popleft()
            for dr, dc in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                nr, nc = r + dr, c + dc
                if 0 <= nr < m and 0 <= nc < n and rooms[nr][nc] == INF:
                    rooms[nr][nc] = rooms[r][c] + 1
                    q.append((nr, nc))
# @lc code=end

