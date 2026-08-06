#
# @lc app=leetcode id=1040 lang=python3
#
# [1040] Moving Stones Until Consecutive II
#
# https://leetcode.com/problems/moving-stones-until-consecutive-ii/description/
#
# algorithms
# Medium (59.23%)
# Likes:    411
# Dislikes: 774
# Total Accepted:    16.1K
# Total Submissions: 27.1K
# Testcase Example:  "[7,4,9]"
#
# There are some stones in different positions on the X-axis. You are given an
# integer array stones, the positions of the stones.
#
# Call a stone an endpoint stone if it has the smallest or largest position. In
# one move, you pick up an endpoint stone and move it to an unoccupied position
# so that it is no longer an endpoint stone.
#
# In particular, if the stones are at say, stones = [1,2,5], you cannot move
# the endpoint stone at position 5, since moving it to any position (such as 0,
# or 3) will still keep that stone as an endpoint stone.
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
# Input: stones = [7,4,9]
# Output: [1,2]
# Explanation: We can move 4 -> 8 for one move to finish the game.
# Or, we can move 9 -> 5, 4 -> 6 for two moves to finish the game.
#
# Example 2:
#
# Input: stones = [6,5,4,3,10]
# Output: [2,3]
# Explanation: We can move 3 -> 8 then 10 -> 7 to finish the game.
# Or, we can move 3 -> 7, 4 -> 8, 5 -> 9 to finish the game.
# Notice we cannot move 10 -> 2 to finish the game, because that would be an
# illegal move.
#
# Constraints:
#
# 3 <= stones.length <= 10^4
#
# 1 <= stones[i] <= 10^9
#
# All the values of stones are unique.
#

# @lc code=start
from typing import List


class Solution:
    def numMovesStonesII(self, stones: List[int]) -> List[int]:
        """
        Interview explanation:
        Sort stones. Max moves = max(stones[-1]-stones[1], stones[-2]-stones[0]) - (n-2).
        Min moves: sliding window find smallest window of size n containing as
        many stones as possible; special case when almost consecutive except one
        endpoint gap of size >1.

        Algorithm:
        - Sort; n=len
        - max_moves = max(end-second, second_last-start) -(n-2)
        - Two pointers window j-i+1 stones in range of length n; track max stones in such window
        - min_moves = n - max_in_window; handle special case

        Complexity: O(n log n) time, O(1) or O(n) space.
        """
        stones.sort()
        n = len(stones)
        max_moves = max(stones[-1] - stones[1], stones[-2] - stones[0]) - (n - 2)
        min_moves = n
        j = 0
        for i in range(n):
            while j + 1 < n and stones[j + 1] - stones[i] + 1 <= n:
                j += 1
            already = j - i + 1
            if already == n - 1 and stones[j] - stones[i] + 1 == n - 1:
                min_moves = min(min_moves, 2)
            else:
                min_moves = min(min_moves, n - already)
        return [min_moves, max_moves]
# @lc code=end
