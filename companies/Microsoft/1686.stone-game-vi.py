#
# @lc app=leetcode id=1686 lang=python3
#
# [1686] Stone Game VI
#
# https://leetcode.com/problems/stone-game-vi/description/
#
# algorithms
# Medium (61.19%)
# Likes:    907
# Dislikes: 79
# Total Accepted:    30.4K
# Total Submissions: 49.8K
# Testcase Example:  "[1,3]"
#
# Alice and Bob take turns playing a game, with Alice starting first.
#
# There are n stones in a pile. On each player's turn, they can remove a stone
# from the pile and receive points based on the stone's value. Alice and Bob
# may value the stones differently.
#
# You are given two integer arrays of length n, aliceValues and bobValues. Each
# aliceValues[i] and bobValues[i] represents how Alice and Bob, respectively,
# value the i^th stone.
#
# The winner is the person with the most points after all the stones are
# chosen. If both players have the same amount of points, the game results in a
# draw. Both players will play optimally. Both players know the other's values.
#
# Determine the result of the game, and:
#
# If Alice wins, return 1.
#
# If Bob wins, return -1.
#
# If the game results in a draw, return 0.
#
# Example 1:
#
# Input: aliceValues = [1,3], bobValues = [2,1]
# Output: 1
# Explanation:
# If Alice takes stone 1 (0-indexed) first, Alice will receive 3 points.
# Bob can only choose stone 0, and will only receive 2 points.
# Alice wins.
#
# Example 2:
#
# Input: aliceValues = [1,2], bobValues = [3,1]
# Output: 0
# Explanation:
# If Alice takes stone 0, and Bob takes stone 1, they will both have 1 point.
# Draw.
#
# Example 3:
#
# Input: aliceValues = [2,4,3], bobValues = [1,6,7]
# Output: -1
# Explanation:
# Regardless of how Alice plays, Bob will be able to have more points than
# Alice.
# For example, if Alice takes stone 1, Bob can take stone 2, and Alice takes
# stone 0, Alice will have 6 points to Bob's 7.
# Bob wins.
#
# Constraints:
#
# n == aliceValues.length == bobValues.length
#
# 1 <= n <= 10^5
#
# 1 <= aliceValues[i], bobValues[i] <= 100
#

# @lc code=start
from typing import List


class Solution:
    def stoneGameVI(self, aliceValues: List[int], bobValues: List[int]) -> int:
        """
        Interview explanation:
        Taking stone i gives you aliceValues[i] (Alice) or bobValues[i] (Bob)
        and denies the other. Optimal: take stones by alice[i]+bob[i] descending
        (value of taking vs opponent taking).

        Algorithm (greedy sort):
        - Sort indices by a[i]+b[i] desc; Alice/Bob alternate summing their values.
        - Compare scores → 1 / -1 / 0.

        Complexity: O(n log n) time, O(n) space.
        """
        n = len(aliceValues)
        order = sorted(range(n), key=lambda i: aliceValues[i] + bobValues[i], reverse=True)
        alice = bob = 0
        for t, i in enumerate(order):
            if t % 2 == 0:
                alice += aliceValues[i]
            else:
                bob += bobValues[i]
        if alice > bob:
            return 1
        if alice < bob:
            return -1
        return 0
# @lc code=end
