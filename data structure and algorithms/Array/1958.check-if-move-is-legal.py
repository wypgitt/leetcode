#
# @lc app=leetcode id=1958 lang=python3
#
# [1958] Check if Move is Legal
#
# https://leetcode.com/problems/check-if-move-is-legal/description/
#
# algorithms
# Medium (50.04%)
# Likes:    182
# Dislikes: 284
# Total Accepted:    19.0K
# Total Submissions: 37.9K
# Testcase Example:  "[[\".\",\".\",\".\",\"B\",\".\",\".\",\".\",\".\"],[\".\",\".\",\".\",\"W\",\".\",\".\",\".\",\".\"],[\".\",\".\",\".\",\"W\",\".\",\".\",\".\",\".\"],[\".\",\".\",\".\",\"W\",\".\",\".\",\".\",\".\"],[\"W\",\"B\",\"B\",\".\",\"W\",\"W\",\"W\",\"B\"],[\".\",\".\",\".\",\"B\",\".\",\".\",\".\",\".\"],[\".\",\".\",\".\",\"B\",\".\",\".\",\".\",\".\"],[\".\",\".\",\".\",\"W\",\".\",\".\",\".\",\".\"]]"
#
# You are given a 0-indexed 8 x 8 grid board, where board[r][c] represents the
# cell (r, c) on a game board. On the board, free cells are represented by '.',
# white cells are represented by 'W', and black cells are represented by 'B'.
#
# Each move in this game consists of choosing a free cell and changing it to
# the color you are playing as (either white or black). However, a move is only
# legal if, after changing it, the cell becomes the endpoint of a good line
# (horizontal, vertical, or diagonal).
#
# A good line is a line of three or more cells (including the endpoints) where
# the endpoints of the line are one color, and the remaining cells in the
# middle are the opposite color (no cells in the line are free). You can find
# examples for good lines in the figure below:
#
# Given two integers rMove and cMove and a character color representing the
# color you are playing as (white or black), return true if changing cell
# (rMove, cMove) to color color is a legal move, or false if it is not legal.
#
# Example 1:
#
# Input: board =
# [[".",".",".","B",".",".",".","."],[".",".",".","W",".",".",".","."],[".",".",".","W",".",".",".","."],[".",".",".","W",".",".",".","."],["W","B","B",".","W","W","W","B"],[".",".",".","B",".",".",".","."],[".",".",".","B",".",".",".","."],[".",".",".","W",".",".",".","."]],
# rMove = 4, cMove = 3, color = "B"
# Output: true
# Explanation: '.', 'W', and 'B' are represented by the colors blue, white, and
# black respectively, and cell (rMove, cMove) is marked with an 'X'.
# The two good lines with the chosen cell as an endpoint are annotated above
# with the red rectangles.
#
# Example 2:
#
# Input: board =
# [[".",".",".",".",".",".",".","."],[".","B",".",".","W",".",".","."],[".",".","W",".",".",".",".","."],[".",".",".","W","B",".",".","."],[".",".",".",".",".",".",".","."],[".",".",".",".","B","W",".","."],[".",".",".",".",".",".","W","."],[".",".",".",".",".",".",".","B"]],
# rMove = 4, cMove = 4, color = "W"
# Output: false
# Explanation: While there are good lines with the chosen cell as a middle
# cell, there are no good lines with the chosen cell as an endpoint.
#
# Constraints:
#
# board.length == board[r].length == 8
#
# 0 <= rMove, cMove < 8
#
# board[rMove][cMove] == '.'
#
# color is either 'B' or 'W'.
#

# @lc code=start
from typing import List


class Solution:
    def checkMove(self, board: List[List[str]], rMove: int, cMove: int, color: str) -> bool:
        """
        Interview explanation:
        Legal if some of 8 directions forms a good line: at least one opposite
        color, then same-color endpoint (Othello-style).

        Algorithm:
        - For each (dr,dc), require first cell opposite, continue on opposite,
          then hit `color`.

        Complexity: O(1) for 8x8 board.
        """
        opp = "W" if color == "B" else "B"
        dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 1), (1, -1), (1, 0), (1, 1)]

        def good(dr: int, dc: int) -> bool:
            r, c = rMove + dr, cMove + dc
            if not (0 <= r < 8 and 0 <= c < 8) or board[r][c] != opp:
                return False
            r += dr
            c += dc
            while 0 <= r < 8 and 0 <= c < 8:
                if board[r][c] == ".":
                    return False
                if board[r][c] == color:
                    return True
                r += dr
                c += dc
            return False

        return any(good(dr, dc) for dr, dc in dirs)

    def checkMove_scan(self, board: List[List[str]], rMove: int, cMove: int, color: str) -> bool:
        """
        Interview explanation:
        Alternate 8-direction scan with seen_opposite flag before endpoint.

        Algorithm:
        - Walk each ray; if hit color after seeing opposite, return True.

        Complexity: O(1) for 8x8 board.
        """
        opp = "W" if color == "B" else "B"
        for dr in (-1, 0, 1):
            for dc in (-1, 0, 1):
                if dr == 0 and dc == 0:
                    continue
                r, c = rMove + dr, cMove + dc
                seen_opp = False
                while 0 <= r < 8 and 0 <= c < 8:
                    if board[r][c] == ".":
                        break
                    if board[r][c] == opp:
                        seen_opp = True
                    elif board[r][c] == color:
                        if seen_opp:
                            return True
                        break
                    r += dr
                    c += dc
        return False
# @lc code=end

