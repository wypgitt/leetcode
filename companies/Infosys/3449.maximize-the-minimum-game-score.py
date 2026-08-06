#
# @lc app=leetcode id=3449 lang=python3
#
# [3449] Maximize the Minimum Game Score
#
# https://leetcode.com/problems/maximize-the-minimum-game-score/description/
#
# algorithms
# Hard (26.72%)
# Likes:    55
# Dislikes: 6
# Total Accepted:    4.6K
# Total Submissions: 17.3K
# Testcase Example:  "[2,4]\n3"
#
#
# You are given an array points of size n and an integer m. There is
# another array gameScore of size n, where gameScore[i] represents the
# score achieved at the i^th game. Initially, gameScore[i] == 0 for all i.
#
# You start at index -1, which is outside the array (before the first
# position at index 0). You can make at most m moves. In each move, you
# can either:
#
# Increase the index by 1 and add points[i] to gameScore[i].
#
# Decrease the index by 1 and add points[i] to gameScore[i].
#
# Note that the index must always remain within the bounds of the array
# after the first move.
#
# Return the maximum possible minimum value in gameScore after at most m
# moves.
#
# Example 1:
#
# Input: points = [2,4], m = 3
#
# Output: 4
#
# Explanation:
#
# Initially, index i = -1 and gameScore = [0, 0].
#
#                         Move
#                         Index
#                         gameScore
#
#                         Increase i
#                         0
#                         [2, 0]
#
#                         Increase i
#                         1
#                         [2, 4]
#
#                         Decrease i
#                         0
#                         [4, 4]
#
# The minimum value in gameScore is 4, and this is the maximum possible
# minimum among all configurations. Hence, 4 is the output.
#
# Example 2:
#
# Input: points = [1,2,3], m = 5
#
# Output: 2
#
# Explanation:
#
# Initially, index i = -1 and gameScore = [0, 0, 0].
#
#                         Move
#                         Index
#                         gameScore
#
#                         Increase i
#                         0
#                         [1, 0, 0]
#
#                         Increase i
#                         1
#                         [1, 2, 0]
#
#                         Decrease i
#                         0
#                         [2, 2, 0]
#
#                         Increase i
#                         1
#                         [2, 4, 0]
#
#                         Increase i
#                         2
#                         [2, 4, 3]
#
# The minimum value in gameScore is 2, and this is the maximum possible
# minimum among all configurations. Hence, 2 is the output.
#
# Constraints:
#
# 2 <= n == points.length <= 5 * 10^4
#
# 1 <= points[i] <= 10^6
#
# 1 <= m <= 10^9
#

# @lc code=start

from typing import List


class Solution:
    def maxScore(self, points: List[int], m: int) -> int:
        """
        Interview explanation:
        Maximize X such that every gameScore[i] >= X using <= m line-walk visits
        (start at -1). Visit i at least ceil(X/points[i]) times.

        Algorithm:
        - Binary search X. Greedy check left-to-right: leftover visits from previous
          index cover part of the requirement; unpaid visits cost 2*need-1 moves
          (round trips with a free last touch), else just walk forward (+1).

        Complexity: O(n log (m*max(points))) time, O(1) space.
        """
        def possible(x: int) -> bool:
            moves = 0
            prev = 0
            n = len(points)
            for i, p in enumerate(points):
                need = (x + p - 1) // p
                need = max(0, need - prev)
                if need > 0:
                    moves += 2 * need - 1
                    prev = need - 1
                elif i + 1 < n:
                    moves += 1
                    prev = 0
                if moves > m:
                    return False
            return True

        lo, hi = 0, (m + 1) // 2 * points[0] + 1
        while lo < hi:
            mid = (lo + hi + 1) // 2
            if possible(mid):
                lo = mid
            else:
                hi = mid - 1
        return lo
# @lc code=end
