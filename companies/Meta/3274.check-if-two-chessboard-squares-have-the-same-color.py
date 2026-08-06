#
# @lc app=leetcode id=3274 lang=python3
#
# [3274] Check if Two Chessboard Squares Have the Same Color
#
# https://leetcode.com/problems/check-if-two-chessboard-squares-have-the-same-color/description/
#
# algorithms
# Easy (72.16%)
# Likes:    148
# Dislikes: 5
# Total Accepted:    73.8K
# Total Submissions: 102.3K
# Testcase Example:  "\"a1\"\n\"c3\""
#
#
# You are given two strings, coordinate1 and coordinate2, representing the
# coordinates of a square on an 8 x 8 chessboard.
#
# Below is the chessboard for reference.
#
# Return true if these two squares have the same color and false
# otherwise.
#
# The coordinate will always represent a valid chessboard square. The
# coordinate will always have the letter first (indicating its column),
# and the number second (indicating its row).
#
# Example 1:
#
# Input: coordinate1 = "a1", coordinate2 = "c3"
#
# Output: true
#
# Explanation:
#
# Both squares are black.
#
# Example 2:
#
# Input: coordinate1 = "a1", coordinate2 = "h3"
#
# Output: false
#
# Explanation:
#
# Square "a1" is black and "h3" is white.
#
# Constraints:
#
# coordinate1.length == coordinate2.length == 2
#
# 'a' <= coordinate1[0], coordinate2[0] <= 'h'
#
# '1' <= coordinate1[1], coordinate2[1] <= '8'
#

# @lc code=start

class Solution:
    def checkTwoChessboards(self, coordinate1: str, coordinate2: str) -> bool:
        """
        Interview explanation:
        Chessboard colors alternate; square (file, rank) is black/white by parity
        of (file_index + rank). Same color iff parities match.

        Algorithm:
        - color(c) = (ord(c[0]) + int(c[1])) & 1; compare both.

        Complexity: O(1) time, O(1) space.
        """
        def color(c: str) -> int:
            return (ord(c[0]) + int(c[1])) & 1

        return color(coordinate1) == color(coordinate2)

    def checkTwoChessboards_diff(self, coordinate1: str, coordinate2: str) -> bool:
        """
        Interview explanation:
        Alternate: same color iff the Manhattan steps between squares is even
        (file delta + rank delta even).

        Algorithm:
        - Return ((ord(f1)-ord(f2)) + (r1-r2)) % 2 == 0.

        Complexity: O(1) time, O(1) space.
        """
        return (
            (ord(coordinate1[0]) - ord(coordinate2[0]))
            + (int(coordinate1[1]) - int(coordinate2[1]))
        ) % 2 == 0
# @lc code=end
