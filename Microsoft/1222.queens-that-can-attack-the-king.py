#
# @lc app=leetcode id=1222 lang=python3
#
# [1222] Queens That Can Attack the King
#
# https://leetcode.com/problems/queens-that-can-attack-the-king/description/
#
# algorithms
# Medium (72.81%)
# Likes:    1008
# Dislikes: 154
# Total Accepted:    52.9K
# Total Submissions: 72.6K
# Testcase Example:  "[[0,1],[1,0],[4,0],[0,4],[3,3],[2,4]]"
#
# On a 0-indexed 8 x 8 chessboard, there can be multiple black queens and one
# white king.
#
# You are given a 2D integer array queens where queens[i] = [xQueen_i,
# yQueen_i] represents the position of the i^th black queen on the chessboard.
# You are also given an integer array king of length 2 where king = [xKing,
# yKing] represents the position of the white king.
#
# Return the coordinates of the black queens that can directly attack the king.
# You may return the answer in any order.
#
# Example 1:
#
# Input: queens = [[0,1],[1,0],[4,0],[0,4],[3,3],[2,4]], king = [0,0]
# Output: [[0,1],[1,0],[3,3]]
# Explanation: The diagram above shows the three queens that can directly
# attack the king and the three queens that cannot attack the king (i.e.,
# marked with red dashes).
#
# Example 2:
#
# Input: queens = [[0,0],[1,1],[2,2],[3,4],[3,5],[4,4],[4,5]], king = [3,3]
# Output: [[2,2],[3,4],[4,4]]
# Explanation: The diagram above shows the three queens that can directly
# attack the king and the three queens that cannot attack the king (i.e.,
# marked with red dashes).
#
# Constraints:
#
# 1 <= queens.length < 64
#
# queens[i].length == king.length == 2
#
# 0 <= xQueen_i, yQueen_i, xKing, yKing < 8
#
# All the given positions are unique.
#


# @lc code=start
from typing import List

class Solution:
    def queensAttacktheKing(self, queens: List[List[int]], king: List[int]) -> List[List[int]]:
        """
        Interview explanation:
        From king cast rays in 8 directions; first queen on each ray attacks.

        Algorithm:
        - Put queens in a set; for each of 8 dirs walk until board edge; first hit

        Complexity: O(1) board 8x8 / O(q) set build.
        """
        qset = {(r, c) for r, c in queens}
        kr, kc = king
        ans = []
        for dr in (-1, 0, 1):
            for dc in (-1, 0, 1):
                if dr == 0 and dc == 0:
                    continue
                r, c = kr + dr, kc + dc
                while 0 <= r < 8 and 0 <= c < 8:
                    if (r, c) in qset:
                        ans.append([r, c])
                        break
                    r += dr
                    c += dc
        return ans
# @lc code=end
