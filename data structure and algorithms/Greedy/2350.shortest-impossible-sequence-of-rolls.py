#
# @lc app=leetcode id=2350 lang=python3
#
# [2350] Shortest Impossible Sequence of Rolls
#
# https://leetcode.com/problems/shortest-impossible-sequence-of-rolls/description/
#
# algorithms
# Hard (69.18%)
# Likes:    677
# Dislikes: 51
# Total Accepted:    19.5K
# Total Submissions: 28.2K
# Testcase Example:  "[4,2,1,2,3,3,2,4,1]\n4"
#
# You are given an integer array rolls of length n and an integer k. You roll a
# k sided dice numbered from 1 to k, n times, where the result of the i^th roll
# is rolls[i].
#
# Return the length of the shortest sequence of rolls so that there's no such
# subsequence in rolls.
#
# A sequence of rolls of length len is the result of rolling a k sided dice len
# times.
#
#
#
# Example 1:
#
# Input: rolls = [4,2,1,2,3,3,2,4,1], k = 4
# Output: 3
# Explanation: Every sequence of rolls of length 1, [1], [2], [3], [4], can be
# taken from rolls.
# Every sequence of rolls of length 2, [1, 1], [1, 2], ..., [4, 4], can be taken
# from rolls.
# The sequence [1, 4, 2] cannot be taken from rolls, so we return 3.
# Note that there are other sequences that cannot be taken from rolls.
#
# Example 2:
#
# Input: rolls = [1,1,2,2], k = 2
# Output: 2
# Explanation: Every sequence of rolls of length 1, [1], [2], can be taken from
# rolls.
# The sequence [2, 1] cannot be taken from rolls, so we return 2.
# Note that there are other sequences that cannot be taken from rolls but [2, 1]
# is the shortest.
#
# Example 3:
#
# Input: rolls = [1,1,3,2,2,2,3,3], k = 4
# Output: 1
# Explanation: The sequence [4] cannot be taken from rolls, so we return 1.
# Note that there are other sequences that cannot be taken from rolls but [4] is
# the shortest.
#
#
#
# Constraints:
#
#
# n == rolls.length
#
#
# 1 <= n <= 10^5
#
#
# 1 <= rolls[i] <= k <= 10^5
#

# @lc code=start
from typing import List


class Solution:
    def shortestSequence(self, rolls: List[int], k: int) -> int:
        """
        Interview explanation:
        Dice shows faces in `rolls` (values in 1..k). Find length of shortest
        sequence that is NOT a subsequence of rolls.

        Algorithm:
        - Greedy: every time we have seen all k faces since last "complete",
          we can extend every length-(ans) sequence; increment ans and reset
          the seen set. Answer is that count + 1.

        Complexity: O(n) time, O(k) space.
        """
        ans = 1
        seen = set()
        for x in rolls:
            seen.add(x)
            if len(seen) == k:
                ans += 1
                seen.clear()
        return ans
# @lc code=end
