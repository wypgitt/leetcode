#
# @lc app=leetcode id=1275 lang=python3
#
# [1275] Find Winner on a Tic Tac Toe Game
#
# https://leetcode.com/problems/find-winner-on-a-tic-tac-toe-game/description/
#
# algorithms
# Easy (54.67%)
# Likes:    1642
# Dislikes: 370
# Total Accepted:    174K
# Total Submissions: 318K
# Testcase Example:  "[[0,0],[2,0],[1,1],[2,1],[2,2]]"
#
# Tic-tac-toe is played by two players A and B on a 3 x 3 grid. The rules of
# Tic-Tac-Toe are:
#
# Players take turns placing characters into empty squares ' '.
#
# The first player A always places 'X' characters, while the second player B
# always places 'O' characters.
#
# 'X' and 'O' characters are always placed into empty squares, never on filled
# ones.
#
# The game ends when there are three of the same (non-empty) character filling
# any row, column, or diagonal.
#
# The game also ends if all squares are non-empty.
#
# No more moves can be played if the game is over.
#
# Given a 2D integer array moves where moves[i] = [row_i, col_i] indicates that
# the i^th move will be played on grid[row_i][col_i]. return the winner of the
# game if it exists (A or B). In case the game ends in a draw return "Draw". If
# there are still movements to play return "Pending".
#
# You can assume that moves is valid (i.e., it follows the rules of
# Tic-Tac-Toe), the grid is initially empty, and A will play first.
#
# Example 1:
#
# Input: moves = [[0,0],[2,0],[1,1],[2,1],[2,2]]
# Output: "A"
# Explanation: A wins, they always play first.
#
# Example 2:
#
# Input: moves = [[0,0],[1,1],[0,1],[0,2],[1,0],[2,0]]
# Output: "B"
# Explanation: B wins.
#
# Example 3:
#
# Input: moves = [[0,0],[1,1],[2,0],[1,0],[1,2],[2,1],[0,1],[0,2],[2,2]]
# Output: "Draw"
# Explanation: The game ends in a draw since there are no moves to make.
#
# Constraints:
#
# 1 <= moves.length <= 9
#
# moves[i].length == 2
#
# 0 <= row_i, col_i <= 2
#
# There are no repeated elements on moves.
#
# moves follow the rules of tic tac toe.
#

# @lc code=start

from typing import List


class Solution:
    def tictactoe(self, moves: List[List[int]]) -> str:
        """
        Interview explanation:
        Simulate 3x3 tic-tac-toe. A plays odd turns (X), B even (O). After all
        moves check winner; else Pending if board not full else Draw.

        Algorithm:
        - board 3x3 empty; place 'X'/'O' alternating.
        - Check rows/cols/diags for three-in-a-row.
        - If winner return A/B; elif len(moves)<9 Pending else Draw.

        Complexity: O(1) time/space (fixed board).
        """
        board = [[""] * 3 for _ in range(3)]
        for i, (r, c) in enumerate(moves):
            board[r][c] = "X" if i % 2 == 0 else "O"

        def winner(p: str) -> bool:
            lines = board + [list(col) for col in zip(*board)]
            lines.append([board[i][i] for i in range(3)])
            lines.append([board[i][2 - i] for i in range(3)])
            return any(all(cell == p for cell in line) for line in lines)

        if winner("X"):
            return "A"
        if winner("O"):
            return "B"
        return "Pending" if len(moves) < 9 else "Draw"

    def tictactoe_count(self, moves: List[List[int]]) -> str:
        """
        Interview explanation:
        Alternate O(1) counters: rows/cols/diag scores +1 for A, -1 for B;
        |score|==3 means win.

        Algorithm:
        - rows,cols,diag,anti arrays; update per move; check abs==3.

        Complexity: O(1).
        """
        rows = [0] * 3
        cols = [0] * 3
        diag = anti = 0
        for i, (r, c) in enumerate(moves):
            v = 1 if i % 2 == 0 else -1
            rows[r] += v
            cols[c] += v
            if r == c:
                diag += v
            if r + c == 2:
                anti += v
            if 3 in (abs(rows[r]), abs(cols[c]), abs(diag), abs(anti)):
                return "A" if v == 1 else "B"
        return "Pending" if len(moves) < 9 else "Draw"
# @lc code=end
