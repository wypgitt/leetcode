#
# @lc app=leetcode id=1040 lang=python3
#
# [1040] Moving Stones Until Consecutive II
#
# https://leetcode.com/problems/moving-stones-until-consecutive-ii/description/
#
# algorithms
# Medium (58.77%)
# Likes:    408
# Dislikes: 765
# Total Accepted:    15.4K
# Total Submissions: 26.2K
# Testcase Example:  '[7,4,9]'
#
# There are some stones in different positions on the X-axis. You are given an
# integer array stones, the positions of the stones.
# 
# Call a stone an endpoint stone if it has the smallest or largest position. In
# one move, you pick up an endpoint stone and move it to an unoccupied position
# so that it is no longer an endpoint stone.
# 
# 
# In particular, if the stones are at say, stones = [1,2,5], you cannot move
# the endpoint stone at position 5, since moving it to any position (such as 0,
# or 3) will still keep that stone as an endpoint stone.
# 
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
# Input: stones = [7,4,9]
# Output: [1,2]
# Explanation: We can move 4 -> 8 for one move to finish the game.
# Or, we can move 9 -> 5, 4 -> 6 for two moves to finish the game.
# 
# 
# Example 2:
# 
# 
# Input: stones = [6,5,4,3,10]
# Output: [2,3]
# Explanation: We can move 3 -> 8 then 10 -> 7 to finish the game.
# Or, we can move 3 -> 7, 4 -> 8, 5 -> 9 to finish the game.
# Notice we cannot move 10 -> 2 to finish the game, because that would be an
# illegal move.
# 
# 
# 
# Constraints:
# 
# 
# 3 <= stones.length <= 10^4
# 1 <= stones[i] <= 10^9
# All the values of stones are unique.
# 
# 
#

# @lc code=start
from typing import List


class Solution:
    def numMovesStonesII(self, stones: List[int]) -> List[int]:
        stones.sort()
        n = len(stones)

        max_moves = max(
            stones[-1] - stones[1] + 1 - (n - 1),
            stones[-2] - stones[0] + 1 - (n - 1),
        )

        min_moves = n
        left = 0
        for right in range(n):
            while stones[right] - stones[left] + 1 > n:
                left += 1

            stones_in_window = right - left + 1
            window_size = stones[right] - stones[left] + 1

            if stones_in_window == n - 1 and window_size == n - 1:
                min_moves = min(min_moves, 2)
            else:
                min_moves = min(min_moves, n - stones_in_window)

        return [min_moves, max_moves]
# @lc code=end

"""
Interview Explanation

Core idea:
The final arrangement is n consecutive positions. For the minimum, find the
window of length n positions that already contains the most stones; all stones
outside that window must move in. For the maximum, leave one endpoint fixed
and count empty spaces that can be filled one move at a time.

Algorithm:
Minimum:
1. Sort stones.
2. Use a sliding window where stones[right] - stones[left] + 1 <= n.
3. The window describes a possible final block of n consecutive positions.
4. If it contains k stones, normally n - k moves are needed.
5. Handle the special case with n - 1 stones packed into n - 1 positions; the
   lone endpoint cannot move directly to the missing endpoint slot, so it
   needs 2 moves.

Maximum:
Either the leftmost or rightmost stone is the final stone left outside the
first compacting range. Count empty positions after excluding one endpoint and
take the larger count.

Data structure choice:
Sorting gives the geometric order. The two-pointer window is ideal because
both endpoints only move forward.

Correctness:
Any final consecutive block has length n, so the stones already inside such a
block can stay and all outside stones must move. The sliding window finds the
block with the most stones already inside, minimizing moves, with the known
endpoint legality exception handled separately. For maximum moves, delaying
completion means filling empty spaces while keeping one endpoint excluded; the
two formulas count the empty spaces for excluding the left or right endpoint.

Complexity:
Sorting costs O(n log n). The sliding window is O(n). Extra space is O(1)
besides the in-place sort.

Tests and edge cases:
- Already consecutive: min and max are 0.
- Almost consecutive like [1,2,3,4,10]: special minimum is 2.
- Large coordinates are safe because only differences are used.
- n = 3 works with the same formulas.
"""
