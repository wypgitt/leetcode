#
# @lc app=leetcode id=1222 lang=python3
#
# [1222] Queens That Can Attack the King
#
# https://leetcode.com/problems/queens-that-can-attack-the-king/description/
#
# algorithms
# Medium (72.64%)
# Likes:    1006
# Dislikes: 154
# Total Accepted:    51.6K
# Total Submissions: 71K
# Testcase Example:  '[[0,1],[1,0],[4,0],[0,4],[3,3],[2,4]]\n[0,0]'
#
# On a 0-indexed 8 x 8 chessboard, there can be multiple black queens and one
# white king.
# 
# You are given a 2D integer array queens where queens[i] = [xQueeni, yQueeni]
# represents the position of the i^th black queen on the chessboard. You are
# also given an integer array king of length 2 where king = [xKing, yKing]
# represents the position of the white king.
# 
# Return the coordinates of the black queens that can directly attack the king.
# You may return the answer in any order.
# 
# 
# Example 1:
# 
# 
# Input: queens = [[0,1],[1,0],[4,0],[0,4],[3,3],[2,4]], king = [0,0]
# Output: [[0,1],[1,0],[3,3]]
# Explanation: The diagram above shows the three queens that can directly
# attack the king and the three queens that cannot attack the king (i.e.,
# marked with red dashes).
# 
# 
# Example 2:
# 
# 
# Input: queens = [[0,0],[1,1],[2,2],[3,4],[3,5],[4,4],[4,5]], king = [3,3]
# Output: [[2,2],[3,4],[4,4]]
# Explanation: The diagram above shows the three queens that can directly
# attack the king and the three queens that cannot attack the king (i.e.,
# marked with red dashes).
# 
# 
# 
# Constraints:
# 
# 
# 1 <= queens.length < 64
# queens[i].length == king.length == 2
# 0 <= xQueeni, yQueeni, xKing, yKing < 8
# All the given positions are unique.
# 
# 
#

# @lc code=start
from typing import List


class Solution:
    def queensAttacktheKing(self, queens: List[List[int]], king: List[int]) -> List[List[int]]:
        occupied = {(row, col) for row, col in queens}
        row, col = king
        attackers = []

        for dr, dc in (
            (1, 0),
            (-1, 0),
            (0, 1),
            (0, -1),
            (1, 1),
            (1, -1),
            (-1, 1),
            (-1, -1),
        ):
            nr, nc = row + dr, col + dc
            while 0 <= nr < 8 and 0 <= nc < 8:
                if (nr, nc) in occupied:
                    attackers.append([nr, nc])
                    break
                nr += dr
                nc += dc

        return attackers
# @lc code=end

# Explanation
# -----------
# A queen attacks the king if it is the first queen encountered in one of the
# eight straight-line directions from the king. Put all queen coordinates in a
# set, then walk one square at a time in each direction until leaving the board
# or finding a queen.
#
# The set gives O(1)-average coordinate lookup, and scanning from the king
# automatically ignores queens blocked by closer queens.
#
# Edge cases: no queen in a direction; multiple queens in one direction only
# the nearest counts; queens on diagonals and rows/columns are all covered by
# the same directional loop.
#
# Time complexity: O(8 * 8), effectively O(1), because the board is fixed.
# Space complexity: O(q) for the queen set.
