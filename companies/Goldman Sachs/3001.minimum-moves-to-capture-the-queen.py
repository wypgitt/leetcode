#
# @lc app=leetcode id=3001 lang=python3
#
# [3001] Minimum Moves to Capture The Queen
#
# https://leetcode.com/problems/minimum-moves-to-capture-the-queen/description/
#
# algorithms
# Medium (22.65%)
# Likes:    188
# Dislikes: 210
# Total Accepted:    23.7K
# Total Submissions: 104.6K
# Testcase Example:  "1\n1\n8\n8\n2\n3"
#
#
# There is a 1-indexed 8 x 8 chessboard containing 3 pieces.
#
# You are given 6 integers a, b, c, d, e, and f where:
#
# (a, b) denotes the position of the white rook.
#
# (c, d) denotes the position of the white bishop.
#
# (e, f) denotes the position of the black queen.
#
# Given that you can only move the white pieces, return the minimum number
# of moves required to capture the black queen.
#
# Note that:
#
# Rooks can move any number of squares either vertically or horizontally,
# but cannot jump over other pieces.
#
# Bishops can move any number of squares diagonally, but cannot jump over
# other pieces.
#
# A rook or a bishop can capture the queen if it is located in a square
# that they can move to.
#
# The queen does not move.
#
# Example 1:
#
# Input: a = 1, b = 1, c = 8, d = 8, e = 2, f = 3
# Output: 2
# Explanation: We can capture the black queen in two moves by moving the
# white rook to (1, 3) then to (2, 3).
# It is impossible to capture the black queen in less than two moves since
# it is not being attacked by any of the pieces at the beginning.
#
# Example 2:
#
# Input: a = 5, b = 3, c = 3, d = 4, e = 5, f = 2
# Output: 1
# Explanation: We can capture the black queen in a single move by doing
# one of the following:
# - Move the white rook to (5, 2).
# - Move the white bishop to (5, 2).
#
# Constraints:
#
# 1 <= a, b, c, d, e, f <= 8
#
# No two pieces are on the same square.
#

# @lc code=start

class Solution:
    def minMovesToCaptureTheQueen(self, a: int, b: int, c: int, d: int, e: int, f: int) -> int:
        """
        Interview explanation:
        On an 8x8 board, white rook/bishop try to capture a static black queen.
        A piece captures in one move if it attacks the queen and the other white
        piece does not block the ray; otherwise the rook always finishes in two.

        Algorithm:
        - Helper: whether (bx, by) lies strictly between two collinear squares.
        - If rook shares row/col with queen and bishop does not block, return 1.
        - If bishop shares a diagonal with queen and rook does not block, return 1.
        - Otherwise return 2.

        Complexity: O(1) time, O(1) space.
        """
        def blocked(x1: int, y1: int, x2: int, y2: int, bx: int, by: int) -> bool:
            if x1 == x2 == bx:
                return min(y1, y2) < by < max(y1, y2)
            if y1 == y2 == by:
                return min(x1, x2) < bx < max(x1, x2)
            if (
                abs(x1 - x2) == abs(y1 - y2)
                and abs(x1 - bx) == abs(y1 - by)
                and abs(x2 - bx) == abs(y2 - by)
            ):
                return min(x1, x2) < bx < max(x1, x2)
            return False

        if (a == e or b == f) and not blocked(a, b, e, f, c, d):
            return 1
        if abs(c - e) == abs(d - f) and not blocked(c, d, e, f, a, b):
            return 1
        return 2
# @lc code=end
