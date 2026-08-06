#
# @lc app=leetcode id=999 lang=python3
#
# [999] Available Captures for Rook
#
# https://leetcode.com/problems/available-captures-for-rook/description/
#
# algorithms
# Easy (72.02%)
# Likes:    820
# Dislikes: 650
# Total Accepted:    93.5K
# Total Submissions: 130K
# Testcase Example:  "[[\".\",\".\",\".\",\".\",\".\",\".\",\".\",\".\"],[\".\",\".\",\".\",\"p\",\".\",\".\",\".\",\".\"],[\".\",\".\",\".\",\"R\",\".\",\".\",\".\",\"p\"],[\".\",\".\",\".\",\".\",\".\",\".\",\".\",\".\"],[\".\",\".\",\".\",\".\",\".\",\".\",\".\",\".\"],[\".\",\".\",\".\",\"p\",\".\",\".\",\".\",\".\"],[\".\",\".\",\".\",\".\",\".\",\".\",\".\",\".\"],[\".\",\".\",\".\",\".\",\".\",\".\",\".\",\".\"]]"
#
# You are given an 8 x 8 matrix representing a chessboard. There is exactly one
# white rook represented by 'R', some number of white bishops 'B', and some
# number of black pawns 'p'. Empty squares are represented by '.'.
#
# A rook can move any number of squares horizontally or vertically (up, down,
# left, right) until it reaches another piece or the edge of the board. A rook
# is attacking a pawn if it can move to the pawn's square in one move.
#
# Note: A rook cannot move through other pieces, such as bishops or pawns. This
# means a rook cannot attack a pawn if there is another piece blocking the
# path.
#
# Return the number of pawns the white rook is attacking.
#
# Example 1:
#
# Input: board =
# [[".",".",".",".",".",".",".","."],[".",".",".","p",".",".",".","."],[".",".",".","R",".",".",".","p"],[".",".",".",".",".",".",".","."],[".",".",".",".",".",".",".","."],[".",".",".","p",".",".",".","."],[".",".",".",".",".",".",".","."],[".",".",".",".",".",".",".","."]]
#
# Output: 3
#
# Explanation:
#
# In this example, the rook is attacking all the pawns.
#
# Example 2:
#
# Input: board =
# [[".",".",".",".",".",".","."],[".","p","p","p","p","p",".","."],[".","p","p","B","p","p",".","."],[".","p","B","R","B","p",".","."],[".","p","p","B","p","p",".","."],[".","p","p","p","p","p",".","."],[".",".",".",".",".",".",".","."],[".",".",".",".",".",".",".","."]]
#
# Output: 0
#
# Explanation:
#
# The bishops are blocking the rook from attacking any of the pawns.
#
# Example 3:
#
# Input: board =
# [[".",".",".",".",".",".",".","."],[".",".",".","p",".",".",".","."],[".",".",".","p",".",".",".","."],["p","p",".","R",".","p","B","."],[".",".",".",".",".",".",".","."],[".",".",".","B",".",".",".","."],[".",".",".","p",".",".",".","."],[".",".",".",".",".",".",".","."]]
#
# Output: 3
#
# Explanation:
#
# The rook is attacking the pawns at positions b5, d6, and f5.
#
# Constraints:
#
# board.length == 8
#
# board[i].length == 8
#
# board[i][j] is either 'R', '.', 'B', or 'p'
#
# There is exactly one cell with board[i][j] == 'R'
#

# @lc code=start
from typing import List


class Solution:
    def numRookCaptures(self, board: List[List[str]]) -> int:
        """
        Interview explanation:
        Find the rook, then scan in four directions until a piece or edge.
        Count 'p' if the first non-empty cell in that ray is a pawn.

        Algorithm:
        - Locate 'R'.
        - For each dir (dr,dc): walk until out of bounds or hit piece; if 'p'
          count += 1; stop on any piece.

        Complexity: O(1) time (8x8), O(1) space.
        """
        rr = rc = 0
        for i in range(8):
            for j in range(8):
                if board[i][j] == "R":
                    rr, rc = i, j
        ans = 0
        for dr, dc in ((-1, 0), (1, 0), (0, -1), (0, 1)):
            r, c = rr + dr, rc + dc
            while 0 <= r < 8 and 0 <= c < 8:
                if board[r][c] == "p":
                    ans += 1
                    break
                if board[r][c] != ".":
                    break
                r += dr
                c += dc
        return ans
# @lc code=end
