#
# @lc app=leetcode id=3096 lang=python3
#
# [3096] Minimum Levels to Gain More Points
#
# https://leetcode.com/problems/minimum-levels-to-gain-more-points/description/
#
# algorithms
# Medium (40.60%)
# Likes:    92
# Dislikes: 32
# Total Accepted:    28.4K
# Total Submissions: 70K
# Testcase Example:  "[1,0,1,0]"
#
#
# You are given a binary array possible of length n.
#
# Alice and Bob are playing a game that consists of n levels. Some of the
# levels in the game are impossible to clear while others can always be
# cleared. In particular, if possible[i] == 0, then the i^th level is
# impossible to clear for both the players. A player gains 1 point on
# clearing a level and loses 1 point if the player fails to clear it.
#
# At the start of the game, Alice will play some levels in the given order
# starting from the 0^th level, after which Bob will play for the rest of
# the levels.
#
# Alice wants to know the minimum number of levels she should play to gain
# more points than Bob, if both players play optimally to maximize their
# points.
#
# Return the minimum number of levels Alice should play to gain more
# points. If this is not possible, return -1.
#
# Note that each player must play at least 1 level.
#
# Example 1:
#
# Input: possible = [1,0,1,0]
#
# Output: 1
#
# Explanation:
#
# Let's look at all the levels that Alice can play up to:
#
# If Alice plays only level 0 and Bob plays the rest of the levels, Alice
# has 1 point, while Bob has -1 + 1 - 1 = -1 point.
#
# If Alice plays till level 1 and Bob plays the rest of the levels, Alice
# has 1 - 1 = 0 points, while Bob has 1 - 1 = 0 points.
#
# If Alice plays till level 2 and Bob plays the rest of the levels, Alice
# has 1 - 1 + 1 = 1 point, while Bob has -1 point.
#
# Alice must play a minimum of 1 level to gain more points.
#
# Example 2:
#
# Input: possible = [1,1,1,1,1]
#
# Output: 3
#
# Explanation:
#
# Let's look at all the levels that Alice can play up to:
#
# If Alice plays only level 0 and Bob plays the rest of the levels, Alice
# has 1 point, while Bob has 4 points.
#
# If Alice plays till level 1 and Bob plays the rest of the levels, Alice
# has 2 points, while Bob has 3 points.
#
# If Alice plays till level 2 and Bob plays the rest of the levels, Alice
# has 3 points, while Bob has 2 points.
#
# If Alice plays till level 3 and Bob plays the rest of the levels, Alice
# has 4 points, while Bob has 1 point.
#
# Alice must play a minimum of 3 levels to gain more points.
#
# Example 3:
#
# Input: possible = [0,0]
#
# Output: -1
#
# Explanation:
#
# The only possible way is for both players to play 1 level each. Alice
# plays level 0 and loses 1 point. Bob plays level 1 and loses 1 point. As
# both players have equal points, Alice can't gain more points than Bob.
#
# Constraints:
#
# 2 <= n == possible.length <= 10^5
#
# possible[i] is either 0 or 1.
#

# @lc code=start
from typing import List


class Solution:
    def minimumLevels(self, possible: List[int]) -> int:
        """
        Interview explanation:
        Score +1 for clearable levels, -1 otherwise. Alice takes a prefix, Bob
        the suffix; both need >= 1 level. Minimize Alice's length with score_A > score_B.

        Algorithm:
        - Convert to scores; prefix Alice vs total - Alice; first index that wins.

        Complexity: O(n) time, O(1) space.
        """
        total = sum(1 if p else -1 for p in possible)
        alice = 0
        for i in range(len(possible) - 1):
            alice += 1 if possible[i] else -1
            if alice > total - alice:
                return i + 1
        return -1
# @lc code=end
