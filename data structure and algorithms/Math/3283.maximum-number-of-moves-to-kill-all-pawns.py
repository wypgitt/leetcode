#
# @lc app=leetcode id=3283 lang=python3
#
# [3283] Maximum Number of Moves to Kill All Pawns
#
# https://leetcode.com/problems/maximum-number-of-moves-to-kill-all-pawns/description/
#
# algorithms
# Hard (34.46%)
# Likes:    152
# Dislikes: 12
# Total Accepted:    7.6K
# Total Submissions: 22.2K
# Testcase Example:  "1\n1\n[[0,0]]"
#
#
# There is a 50 x 50 chessboard with one knight and some pawns on it. You
# are given two integers kx and ky where (kx, ky) denotes the position of
# the knight, and a 2D array positions where positions[i] = [x_i, y_i]
# denotes the position of the pawns on the chessboard.
#
# Alice and Bob play a turn-based game, where Alice goes first. In each
# player's turn:
#
# The player selects a pawn that still exists on the board and captures it
# with the knight in the fewest possible moves. Note that the player can
# select any pawn, it might not be one that can be captured in the least
# number of moves.
#
# In the process of capturing the selected pawn, the knight may pass other
# pawns without capturing them. Only the selected pawn can be captured in
# this turn.
#
# Alice is trying to maximize the sum of the number of moves made by both
# players until there are no more pawns on the board, whereas Bob tries to
# minimize them.
#
# Return the maximum total number of moves made during the game that Alice
# can achieve, assuming both players play optimally.
#
# Note that in one move, a chess knight has eight possible positions it
# can move to, as illustrated below. Each move is two cells in a cardinal
# direction, then one cell in an orthogonal direction.
#
# Example 1:
#
# Input: kx = 1, ky = 1, positions = [[0,0]]
#
# Output: 4
#
# Explanation:
#
# The knight takes 4 moves to reach the pawn at (0, 0).
#
# Example 2:
#
# Input: kx = 0, ky = 2, positions = [[1,1],[2,2],[3,3]]
#
# Output: 8
#
# Explanation:
#
# Alice picks the pawn at (2, 2) and captures it in two moves: (0, 2) ->
# (1, 4) -> (2, 2).
#
# Bob picks the pawn at (3, 3) and captures it in two moves: (2, 2) -> (4,
# 1) -> (3, 3).
#
# Alice picks the pawn at (1, 1) and captures it in four moves: (3, 3) ->
# (4, 1) -> (2, 2) -> (0, 3) -> (1, 1).
#
# Example 3:
#
# Input: kx = 0, ky = 0, positions = [[1,2],[2,4]]
#
# Output: 3
#
# Explanation:
#
# Alice picks the pawn at (2, 4) and captures it in two moves: (0, 0) ->
# (1, 2) -> (2, 4). Note that the pawn at (1, 2) is not captured.
#
# Bob picks the pawn at (1, 2) and captures it in one move: (2, 4) -> (1,
# 2).
#
# Constraints:
#
# 0 <= kx, ky <= 49
#
# 1 <= positions.length <= 15
#
# positions[i].length == 2
#
# 0 <= positions[i][0], positions[i][1] <= 49
#
# All positions[i] are unique.
#
# The input is generated such that positions[i] != [kx, ky] for all 0 <= i
# < positions.length.
#

# @lc code=start
from collections import deque
from functools import lru_cache
from typing import List


class Solution:
    def maxMoves(self, kx: int, ky: int, positions: List[List[int]]) -> int:
        """
        Interview explanation:
        Knight captures on a 50x50 board; Alice maximizes total knight moves,
        Bob minimizes, both optimal. Few pawns (n<=15) → subset DP + distances.

        Algorithm:
        - BFS knight distances between start and every pawn pair.
        - DP(mask, pos, alice): remaining pawns are unset bits; knight at pos.
        - Alice takes max over next pawn, Bob takes min; add dist[pos][next].

        Complexity: O(n^2 * 50^2 + n^2 * 2^n) time, O(n^2 + n * 2^n) space.
        """
        n = len(positions)
        pts = positions + [[kx, ky]]
        knight = [
            (1, 2), (1, -2), (-1, 2), (-1, -2),
            (2, 1), (2, -1), (-2, 1), (-2, -1),
        ]
        dist = [[0] * (n + 1) for _ in range(n + 1)]
        for i in range(n + 1):
            sx, sy = pts[i]
            dmap = [[-1] * 50 for _ in range(50)]
            q = deque([(sx, sy)])
            dmap[sx][sy] = 0
            while q:
                x, y = q.popleft()
                for dx, dy in knight:
                    nx, ny = x + dx, y + dy
                    if 0 <= nx < 50 and 0 <= ny < 50 and dmap[nx][ny] < 0:
                        dmap[nx][ny] = dmap[x][y] + 1
                        q.append((nx, ny))
            for j in range(n + 1):
                dist[i][j] = dmap[pts[j][0]][pts[j][1]]

        full = (1 << n) - 1

        @lru_cache(None)
        def dp(mask: int, pos: int, alice: bool) -> int:
            if mask == full:
                return 0
            if alice:
                best = 0
                for i in range(n):
                    if mask >> i & 1:
                        continue
                    best = max(best, dist[pos][i] + dp(mask | (1 << i), i, False))
                return best
            best = 10**9
            for i in range(n):
                if mask >> i & 1:
                    continue
                best = min(best, dist[pos][i] + dp(mask | (1 << i), i, True))
            return best

        return dp(0, n, True)
# @lc code=end
