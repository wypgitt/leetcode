#
# @lc app=leetcode id=1033 lang=python3
#
# [1033] Moving Stones Until Consecutive
#
# https://leetcode.com/problems/moving-stones-until-consecutive/description/
#
# algorithms
# Medium (52.27%)
# Likes:    258
# Dislikes: 658
# Total Accepted:    34.7K
# Total Submissions: 66.3K
# Testcase Example:  '1\n2\n5'
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
# 
# answer[0] is the minimum number of moves you can play, and
# answer[1] is the maximum number of moves you can play.
# 
# 
# 
# Example 1:
# 
# 
# Input: a = 1, b = 2, c = 5
# Output: [1,2]
# Explanation: Move the stone from 5 to 3, or move the stone from 5 to 4 to
# 3.
# 
# 
# Example 2:
# 
# 
# Input: a = 4, b = 3, c = 2
# Output: [0,0]
# Explanation: We cannot make any moves.
# 
# 
# Example 3:
# 
# 
# Input: a = 3, b = 5, c = 1
# Output: [1,2]
# Explanation: Move the stone from 1 to 4; or move the stone from 1 to 2 to
# 4.
# 
# 
# 
# Constraints:
# 
# 
# 1 <= a, b, c <= 100
# a, b, and c have different values.
# 
# 
#

# @lc code=start
from typing import List


class Solution:
    def numMovesStones(self, a: int, b: int, c: int) -> List[int]:
        x, y, z = sorted((a, b, c))

        max_moves = z - x - 2

        if y == x + 1 and z == y + 1:
            min_moves = 0
        elif y - x <= 2 or z - y <= 2:
            min_moves = 1
        else:
            min_moves = 2

        return [min_moves, max_moves]
# @lc code=end

"""
Interview Explanation

Core idea:
With only three stones, the state is fully described by the two gaps after
sorting. The final state requires both gaps to be 1.

Algorithm:
1. Sort positions as x < y < z.
2. Maximum moves: keep moving an endpoint into the larger open interval one
   step at a time. There are z - x - 2 empty positions between endpoints, so
   that is the maximum.
3. Minimum moves:
   - Already consecutive: 0.
   - If either gap is 1 or 2, one endpoint can move directly to finish.
   - Otherwise, both outer stones need to move: 2.

Data structure choice:
No advanced structure is needed; sorting three values exposes all relevant
geometry.

Correctness:
For the minimum, one move can only relocate one endpoint. If the stones are
already consecutive, no move is needed. If a gap is at most 2, the missing
position beside the close pair can be filled by moving the opposite endpoint,
ending the game. If both gaps exceed 2, no single endpoint move can make both
gaps equal to 1, so two moves are necessary and sufficient. The maximum counts
all interior empty positions that can be consumed before the stones become
consecutive.

Complexity:
O(1) time and O(1) space.

Tests and edge cases:
- Already consecutive, e.g. 2, 3, 4 -> [0, 0].
- One missing spot, e.g. 1, 2, 4 -> minimum 1.
- Symmetric gaps, e.g. 1, 3, 5 -> minimum 1, maximum 2.
- Unsorted input is handled by sorting first.
"""
