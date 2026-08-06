#
# @lc app=leetcode id=2814 lang=python3
#
# [2814] Minimum Time Takes to Reach Destination Without Drowning
#
# https://leetcode.com/problems/minimum-time-takes-to-reach-destination-without-drowning/description/
#
# algorithms
# Hard (54.25%)
# Likes:    25
# Dislikes: 2
# Total Accepted:    1.6K
# Total Submissions: 3K
# Testcase Example:  "[[\"D\",\".\",\"*\"],[\".\",\".\",\".\"],[\".\",\"S\",\".\"]]"
#
#
# You are given an n * m 0-indexed grid of string land. Right now, you are
# standing at the cell that contains "S", and you want to get to the cell
# containing "D". There are three other types of cells in this land:
#
# ".": These cells are empty.
#
# "X": These cells are stone.
#
# "*": These cells are flooded.
#
# At each second, you can move to a cell that shares a side with your
# current cell (if it exists). Also, at each second, every empty cell that
# shares a side with a flooded cell becomes flooded as well.
#
# There are two problems ahead of your journey:
#
# You can't step on stone cells.
#
# You can't step on flooded cells since you will drown (also, you can't
# step on a cell that will be flooded at the same time as you step on it).
#
# Return the minimum time it takes you to reach the destination in
# seconds, or -1 if it is impossible.
#
# Note that the destination will never be flooded.
#
# Example 1:
#
# Input: land = [["D",".","*"],[".",".","."],[".","S","."]]
# Output: 3
# Explanation: The picture below shows the simulation of the land second
# by second. The blue cells are flooded, and the gray cells are stone.
# Picture (0) shows the initial state and picture (3) shows the final
# state when we reach destination. As you see, it takes us 3 second to
# reach destination and the answer would be 3.
# It can be shown that 3 is the minimum time needed to reach from S to D.
#
# Example 2:
#
# Input: land = [["D","X","*"],[".",".","."],[".",".","S"]]
# Output: -1
# Explanation: The picture below shows the simulation of the land second
# by second. The blue cells are flooded, and the gray cells are stone.
# Picture (0) shows the initial state. As you see, no matter which paths
# we choose, we will drown at the 3^rd second. Also the minimum path takes
# us 4 seconds to reach from S to D.
# So the answer would be -1.
#
# Example 3:
#
# Input: land =
# [["D",".",".",".","*","."],[".","X",".","X",".","."],[".",".",".",".","S","."]]
# Output: 6
# Explanation: It can be shown that we can reach destination in 6 seconds.
# Also it can be shown that 6 is the minimum seconds one need to reach
# from S to D.
#
# Constraints:
#
# 2 <= n, m <= 100
#
# land consists only of "S", "D", ".", "*" and "X".
#
# Exactly one of the cells is equal to "S".
#
# Exactly one of the cells is equal to "D".
#
# @lc code=start
from collections import deque
from itertools import pairwise
from math import inf
from typing import List


class Solution:
    def minimumSeconds(self, land: List[List[str]]) -> int:
        """
        Interview explanation:
        Premium: grid with S, D, '.', 'X' (stone), '*' (flood). Flood spreads
        to adjacent empty/S cells each second. Move 4-dir each second; cannot
        step on stone or a cell that is/will be flooded at arrival time.
        D never floods. Return min time S->D or -1.

        Algorithm:
        - Multi-source BFS from all '*' to get earliest flood time g[r][c].
        - BFS from S: move to '.'/'D' with g[nr][nc] > arrival_time.

        Complexity: O(mn) time, O(mn) space.
        """
        m, n = len(land), len(land[0])
        vis = [[False] * n for _ in range(m)]
        g = [[inf] * n for _ in range(m)]
        q: deque = deque()
        si = sj = 0
        for i, row in enumerate(land):
            for j, c in enumerate(row):
                if c == "*":
                    q.append((i, j))
                elif c == "S":
                    si, sj = i, j
        dirs = (-1, 0, 1, 0, -1)
        t = 0
        while q:
            for _ in range(len(q)):
                i, j = q.popleft()
                g[i][j] = t
                for a, b in pairwise(dirs):
                    x, y = i + a, j + b
                    if (
                        0 <= x < m
                        and 0 <= y < n
                        and not vis[x][y]
                        and land[x][y] in ".S"
                    ):
                        vis[x][y] = True
                        q.append((x, y))
            t += 1
        t = 0
        q = deque([(si, sj)])
        vis = [[False] * n for _ in range(m)]
        vis[si][sj] = True
        while q:
            for _ in range(len(q)):
                i, j = q.popleft()
                if land[i][j] == "D":
                    return t
                for a, b in pairwise(dirs):
                    x, y = i + a, j + b
                    if (
                        0 <= x < m
                        and 0 <= y < n
                        and g[x][y] > t + 1
                        and not vis[x][y]
                        and land[x][y] in ".D"
                    ):
                        vis[x][y] = True
                        q.append((x, y))
            t += 1
        return -1
# @lc code=end
