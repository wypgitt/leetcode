#
# @lc app=leetcode id=2056 lang=python3
#
# [2056] Number of Valid Move Combinations On Chessboard
#
# https://leetcode.com/problems/number-of-valid-move-combinations-on-chessboard/description/
#
# algorithms
# Hard (48.27%)
# Likes:    79
# Dislikes: 298
# Total Accepted:    6K
# Total Submissions: 12.5K
# Testcase Example:  "[\"rook\"]\n[[1,1]]"
#
# There is an 8 x 8 chessboard containing n pieces (rooks, queens, or bishops).
# You are given a string array pieces of length n, where pieces[i] describes the
# type (rook, queen, or bishop) of the i^th piece. In addition, you are given a
# 2D integer array positions also of length n, where positions[i] = [r_i, c_i]
# indicates that the i^th piece is currently at the 1-based coordinate (r_i,
# c_i) on the chessboard.
#
# When making a move for a piece, you choose a destination square that the piece
# will travel toward and stop on.
#
#
# A rook can only travel horizontally or vertically from (r, c) to the direction
# of (r+1, c), (r-1, c), (r, c+1), or (r, c-1).
#
#
# A queen can only travel horizontally, vertically, or diagonally from (r, c) to
# the direction of (r+1, c), (r-1, c), (r, c+1), (r, c-1), (r+1, c+1), (r+1,
# c-1), (r-1, c+1), (r-1, c-1).
#
#
# A bishop can only travel diagonally from (r, c) to the direction of (r+1,
# c+1), (r+1, c-1), (r-1, c+1), (r-1, c-1).
#
# You must make a move for every piece on the board simultaneously. A move
# combination consists of all the moves performed on all the given pieces. Every
# second, each piece will instantaneously travel one square towards their
# destination if they are not already at it. All pieces start traveling at the
# 0^th second. A move combination is invalid if, at a given time, two or more
# pieces occupy the same square.
#
# Return the number of valid move combinations​​​​​.
#
# Notes:
#
#
# No two pieces will start in the same square.
#
#
# You may choose the square a piece is already on as its destination.
#
#
# If two pieces are directly adjacent to each other, it is valid for them to
# move past each other and swap positions in one second.
#
#
#
# Example 1:
#
# Input: pieces = ["rook"], positions = [[1,1]]
# Output: 15
# Explanation: The image above shows the possible squares the piece can move to.
#
# Example 2:
#
# Input: pieces = ["queen"], positions = [[1,1]]
# Output: 22
# Explanation: The image above shows the possible squares the piece can move to.
#
# Example 3:
#
# Input: pieces = ["bishop"], positions = [[4,3]]
# Output: 12
# Explanation: The image above shows the possible squares the piece can move to.
#
#
#
# Constraints:
#
#
# n == pieces.length
#
#
# n == positions.length
#
#
# 1 <= n <= 4
#
#
# pieces only contains the strings "rook", "queen", and "bishop".
#
#
# There will be at most one queen on the chessboard.
#
#
# 1 <= r_i, c_i <= 8
#
#
# Each positions[i] is distinct.
#

# @lc code=start
from typing import List


class Solution:
    def countCombinations(self, pieces: List[str], positions: List[List[int]]) -> int:
        """
        Interview explanation:
        Count valid simultaneous move combinations for chess pieces (rook/queen/
        bishop) on an 8x8 board. Each piece may stay or move any number of
        squares in allowed directions in one move; pieces must not attack the
        same square at the same time (including destination collisions).

        Algorithm:
        - For each piece enumerate all legal single moves (dir, steps) incl. stay.
        - Recursively assign moves; simulate step-by-step positions up to max steps;
          reject if two pieces occupy same cell at any time t.

        Complexity: exponential in #pieces (≤4); constant board size.
        """
        dirs = {
            'rook': [(1, 0), (-1, 0), (0, 1), (0, -1)],
            'bishop': [(1, 1), (1, -1), (-1, 1), (-1, -1)],
            'queen': [(1, 0), (-1, 0), (0, 1), (0, -1), (1, 1), (1, -1), (-1, 1), (-1, -1)],
        }
        n = len(pieces)
        starts = [(r - 1, c - 1) for r, c in positions]
        all_moves = []  # list of list of (dr, dc, steps)

        for i, piece in enumerate(pieces):
            r0, c0 = starts[i]
            moves = [(0, 0, 0)]  # stay
            for dr, dc in dirs[piece]:
                for steps in range(1, 8):
                    nr, nc = r0 + dr * steps, c0 + dc * steps
                    if 0 <= nr < 8 and 0 <= nc < 8:
                        moves.append((dr, dc, steps))
                    else:
                        break
            all_moves.append(moves)

        chosen = [None] * n
        ans = 0

        def pos_at(i: int, t: int):
            dr, dc, steps = chosen[i]
            r0, c0 = starts[i]
            if t >= steps:
                return (r0 + dr * steps, c0 + dc * steps)
            return (r0 + dr * t, c0 + dc * t)

        def valid() -> bool:
            max_t = max(ch[2] for ch in chosen)
            for t in range(1, max_t + 1):
                seen = set()
                for i in range(n):
                    p = pos_at(i, t)
                    if p in seen:
                        return False
                    seen.add(p)
            return True

        def dfs(i: int):
            nonlocal ans
            if i == n:
                if valid():
                    ans += 1
                return
            for mv in all_moves[i]:
                chosen[i] = mv
                dfs(i + 1)

        dfs(0)
        return ans
# @lc code=end
