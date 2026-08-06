#
# @lc app=leetcode id=808 lang=python3
#
# [808] Soup Servings
#
# https://leetcode.com/problems/soup-servings/description/
#
# algorithms
# Medium (59.63%)
# Likes:    1462
# Dislikes: 3953
# Total Accepted:    151K
# Total Submissions: 253.3K
# Testcase Example:  '50'
#
# You have two soups, A and B, each starting with n mL. On every turn, one of
# the following four serving operations is chosen at random, each with
# probability 0.25 independent of all previous turns:
# 
# 
# pour 100 mL from type A and 0 mL from type B
# pour 75 mL from type A and 25 mL from type B
# pour 50 mL from type A and 50 mL from type B
# pour 25 mL from type A and 75 mL from type B
# 
# 
# Note:
# 
# 
# There is no operation that pours 0 mL from A and 100 mL from B.
# The amounts from A and B are poured simultaneously during the turn.
# If an operation asks you to pour more than you have left of a soup, pour all
# that remains of that soup.
# 
# 
# The process stops immediately after any turn in which one of the soups is
# used up.
# 
# Return the probability that A is used up before B, plus half the probability
# that both soups are used up in the same turn. Answers within 10^-5 of the
# actual answer will be accepted.
# 
# 
# Example 1:
# 
# 
# Input: n = 50
# Output: 0.62500
# Explanation: 
# If we perform either of the first two serving operations, soup A will become
# empty first.
# If we perform the third operation, A and B will become empty at the same
# time.
# If we perform the fourth operation, B will become empty first.
# So the total probability of A becoming empty first plus half the probability
# that A and B become empty at the same time, is 0.25 * (1 + 1 + 0.5 + 0) =
# 0.625.
# 
# 
# Example 2:
# 
# 
# Input: n = 100
# Output: 0.71875
# Explanation: 
# If we perform the first serving operation, soup A will become empty first.
# If we perform the second serving operations, A will become empty on
# performing operation [1, 2, 3], and both A and B become empty on performing
# operation 4.
# If we perform the third operation, A will become empty on performing
# operation [1, 2], and both A and B become empty on performing operation 3.
# If we perform the fourth operation, A will become empty on performing
# operation 1, and both A and B become empty on performing operation 2.
# So the total probability of A becoming empty first plus half the probability
# that A and B become empty at the same time, is 0.71875.
# 
# 
# 
# Constraints:
# 
# 
# 0 <= n <= 10^9
# 
# 
#

# @lc code=start
from functools import lru_cache
import math


class Solution:
    def soupServings(self, n: int) -> float:
        if n > 4800:
            return 1.0
        units = math.ceil(n / 25)
        servings = ((4, 0), (3, 1), (2, 2), (1, 3))

        @lru_cache(None)
        def dp(a: int, b: int) -> float:
            if a <= 0 and b <= 0:
                return 0.5
            if a <= 0:
                return 1.0
            if b <= 0:
                return 0.0
            return 0.25 * sum(dp(a - da, b - db) for da, db in servings)

        return dp(units, units)
# @lc code=end

"""
Interview explanation:
All serving amounts are multiples of 25, so scale n to units of 25. Let dp(a,b) be the desired probability with a and b units left. The answer is the average over the four equally likely serving operations, with base cases for A empty first, B empty first, or both empty together.

Data structure: memoized recursion caches probability states.

Edge cases: simultaneous empty contributes 0.5. For large n the probability approaches 1 because A is depleted faster in expectation; 4800 is a standard cutoff within the required 1e-5 error.

Complexity: O(u^2) states for u=ceil(n/25) below the cutoff, each with four transitions. Space is O(u^2).
"""
