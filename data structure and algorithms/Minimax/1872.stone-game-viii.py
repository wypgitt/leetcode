#
# @lc app=leetcode id=1872 lang=python3
#
# [1872] Stone Game VIII
#
# https://leetcode.com/problems/stone-game-viii/description/
#
# algorithms
# Hard (54.22%)
# Likes:    485
# Dislikes: 25
# Total Accepted:    13.9K
# Total Submissions: 25.7K
# Testcase Example:  "[-1,2,-3,4,-5]"
#
# Alice and Bob take turns playing a game, with Alice starting first.
#
# There are n stones arranged in a row. On each player's turn, while the number
# of stones is more than one, they will do the following:
#
# Choose an integer x > 1, and remove the leftmost x stones from the row.
#
# Add the sum of the removed stones' values to the player's score.
#
# Place a new stone, whose value is equal to that sum, on the left side of the
# row.
#
# The game stops when only one stone is left in the row.
#
# The score difference between Alice and Bob is (Alice's score - Bob's score).
# Alice's goal is to maximize the score difference, and Bob's goal is the
# minimize the score difference.
#
# Given an integer array stones of length n where stones[i] represents the
# value of the i^th stone from the left, return the score difference between
# Alice and Bob if they both play optimally.
#
# Example 1:
#
# Input: stones = [-1,2,-3,4,-5]
# Output: 5
# Explanation:
# - Alice removes the first 4 stones, adds (-1) + 2 + (-3) + 4 = 2 to her
# score, and places a stone of
# value 2 on the left. stones = [2,-5].
# - Bob removes the first 2 stones, adds 2 + (-5) = -3 to his score, and places
# a stone of value -3 on
# the left. stones = [-3].
# The difference between their scores is 2 - (-3) = 5.
#
# Example 2:
#
# Input: stones = [7,-6,5,10,5,-2,-6]
# Output: 13
# Explanation:
# - Alice removes all stones, adds 7 + (-6) + 5 + 10 + 5 + (-2) + (-6) = 13 to
# her score, and places a
# stone of value 13 on the left. stones = [13].
# The difference between their scores is 13 - 0 = 13.
#
# Example 3:
#
# Input: stones = [-10,-12]
# Output: -22
# Explanation:
# - Alice can only make one move, which is to remove both stones. She adds
# (-10) + (-12) = -22 to her
# score and places a stone of value -22 on the left. stones = [-22].
# The difference between their scores is (-22) - 0 = -22.
#
# Constraints:
#
# n == stones.length
#
# 2 <= n <= 10^5
#
# -10^4 <= stones[i] <= 10^4
#

# @lc code=start
from typing import List


class Solution:
    def stoneGameVIII(self, stones: List[int]) -> int:
        """
        Interview explanation:
        Players alternately take prefix of ≥2 stones, replace with sum; score
        += that sum. Maximize Alice-Bob difference (both optimal). Prefix sums
        + DP from the right: dp[i] = max score starting when prefix i is forced.

        Algorithm (prefix + suffix max DP):
        - pref[i] = sum(stones[:i+1]).
        - Let f[i] = best score difference when must take a prefix ending ≥ i.
        - f[n-1]=pref[n-1]; f[i]=max(f[i+1], pref[i]-f[i+1]).
        - Answer f[1] (first move takes at least first 2 stones → index ≥1).

        Complexity: O(n) time/space.
        """
        n = len(stones)
        pref = stones[:]
        for i in range(1, n):
            pref[i] += pref[i - 1]
        # dp = best score (current - opponent) when next removal uses prefix end >= i
        dp = pref[-1]
        for i in range(n - 2, 0, -1):
            dp = max(dp, pref[i] - dp)
        return dp
# @lc code=end
