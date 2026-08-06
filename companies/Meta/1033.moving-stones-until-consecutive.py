#
# @lc app=leetcode id=1033 lang=python3
#
# [1033] Moving Stones Until Consecutive
#
# https://leetcode.com/problems/moving-stones-until-consecutive/description/
#
# algorithms
# Medium (52.58%)
# Likes:    260
# Dislikes: 658
# Total Accepted:    35.6K
# Total Submissions: 67.8K
# Testcase Example:  "1"
#
# There are three stones in different positions on the X-axis. You are given
# three integers a, b, and c, the positions of the stones.
#
# In one move, you pick up a stone at an endpoint (i.e., either the lowest or
# highest position stone), and move it to an unoccupied position between those
# endpoints. Formally, let's say the stones are currently at positions x, y,
# and z with x < y < z. You pick up the stone at either position x or position
# z, and move that stone to an integer position k, with x < k < z and k != y.
#
# The game ends when you cannot make any more moves (i.e., the stones are in
# three consecutive positions).
#
# Return an integer array answer of length 2 where:
#
# answer[0] is the minimum number of moves you can play, and
#
# answer[1] is the maximum number of moves you can play.
#
# Example 1:
#
# Input: a = 1, b = 2, c = 5
# Output: [1,2]
# Explanation: Move the stone from 5 to 3, or move the stone from 5 to 4 to 3.
#
# Example 2:
#
# Input: a = 4, b = 3, c = 2
# Output: [0,0]
# Explanation: We cannot make any moves.
#
# Example 3:
#
# Input: a = 3, b = 5, c = 1
# Output: [1,2]
# Explanation: Move the stone from 1 to 4; or move the stone from 1 to 2 to 4.
#
# Constraints:
#
# 1 <= a, b, c <= 100
#
# a, b, and c have different values.
#

# @lc code=start
from typing import List


class Solution:
    def numMovesStones(self, a: int, b: int, c: int) -> List[int]:
        """
        Interview explanation:
        Sort x<y<z. Max moves = z-x-2 (always move endpoints inward one by one).
        Min moves: 0 if already consecutive; 1 if a gap of size 1 or 2 between
        any pair (can finish in one move); else 2.

        Algorithm:
        - x,y,z = sorted
        - mn = 0 if z-x==2 else 1 if y-x<=2 or z-y<=2 else 2
        - mx = z-x-2

        Complexity: O(1) time and space.
        """
        x, y, z = sorted((a, b, c))
        if z - x == 2:
            mn = 0
        elif y - x <= 2 or z - y <= 2:
            mn = 1
        else:
            mn = 2
        return [mn, z - x - 2]
# @lc code=end
