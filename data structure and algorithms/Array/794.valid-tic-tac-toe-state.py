#
# @lc app=leetcode id=794 lang=python3
#
# [794] Valid Tic-Tac-Toe State
#
# https://leetcode.com/problems/valid-tic-tac-toe-state/description/
#
# algorithms
# Medium (34.93%)
# Likes:    591
# Dislikes: 1169
# Total Accepted:    69.4K
# Total Submissions: 199K
# Testcase Example:  "[\"O  \",\"   \",\"   \"]"
#
# Given a Tic-Tac-Toe board as a string array board, return true if and only if
# it is possible to reach this board position during the course of a valid
# tic-tac-toe game.
#
# The board is a 3 x 3 array that consists of characters ' ', 'X', and 'O'. The
# ' ' character represents an empty square.
#
# Here are the rules of Tic-Tac-Toe:
#
# Players take turns placing characters into empty squares ' '.
#
# The first player always places 'X' characters, while the second player always
# places 'O' characters.
#
# 'X' and 'O' characters are always placed into empty squares, never filled
# ones.
#
# The game ends when there are three of the same (non-empty) character filling
# any row, column, or diagonal.
#
# The game also ends if all squares are non-empty.
#
# No more moves can be played if the game is over.
#
# Example 1:
#
# Input: board = ["O "," "," "]
# Output: false
# Explanation: The first player always plays "X".
#
# Example 2:
#
# Input: board = ["XOX"," X "," "]
# Output: false
# Explanation: Players take turns making moves.
#
# Example 3:
#
# Input: board = ["XOX","O O","XOX"]
# Output: true
#
# Constraints:
#
# board.length == 3
#
# board[i].length == 3
#
# board[i][j] is either 'X', 'O', or ' '.
#

# @lc code=start
from typing import List


class Solution:
    def validTicTacToe(self, board: List[str]) -> bool:
        """
        Interview explanation:
        Check if board can arise from valid play: X first; |countX - countO|
        is 0 or 1; both cannot win; if X wins then countX == countO+1; if O
        wins then counts equal.

        Algorithm:
        - Count X/O; reject if countO > countX or countX > countO + 1.
        - Detect wins via rows/cols/diags.
        - Apply win/count constraints above.

        Complexity: O(1) time/space (3×3).
        """
        def win(p: str) -> bool:
            for i in range(3):
                if all(board[i][j] == p for j in range(3)):
                    return True
                if all(board[j][i] == p for j in range(3)):
                    return True
            if all(board[i][i] == p for i in range(3)):
                return True
            if all(board[i][2 - i] == p for i in range(3)):
                return True
            return False

        x = sum(row.count("X") for row in board)
        o = sum(row.count("O") for row in board)
        if o > x or x > o + 1:
            return False
        xwin, owin = win("X"), win("O")
        if xwin and owin:
            return False
        if xwin and x != o + 1:
            return False
        if owin and x != o:
            return False
        return True
# @lc code=end

