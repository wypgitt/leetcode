#
# @lc app=leetcode id=1362 lang=python3
#
# [1362] Closest Divisors
#
# https://leetcode.com/problems/closest-divisors/description/
#
# algorithms
# Medium (62.17%)
# Likes:    339
# Dislikes: 101
# Total Accepted:    29.2K
# Total Submissions: 46.9K
# Testcase Example:  '8'
#
# Given an integer num, find the closest two integers in absolute difference
# whose product equals num + 1 or num + 2.
# 
# Return the two integers in any order.
# 
# 
# Example 1:
# 
# 
# Input: num = 8
# Output: [3,3]
# Explanation: For num + 1 = 9, the closest divisors are 3 & 3, for num + 2 =
# 10, the closest divisors are 2 & 5, hence 3 & 3 is chosen.
# 
# 
# Example 2:
# 
# 
# Input: num = 123
# Output: [5,25]
# 
# 
# Example 3:
# 
# 
# Input: num = 999
# Output: [40,25]
# 
# 
# 
# Constraints:
# 
# 
# 1 <= num <= 10^9
# 
# 
#

# @lc code=start
from __future__ import annotations

from math import isqrt
from typing import List


class Solution:
    def closestDivisors(self, num: int) -> List[int]:
        def closest_pair(value: int) -> List[int]:
            for divisor in range(isqrt(value), 0, -1):
                if value % divisor == 0:
                    return [divisor, value // divisor]
            return [1, value]

        pair1 = closest_pair(num + 1)
        pair2 = closest_pair(num + 2)

        if abs(pair1[0] - pair1[1]) <= abs(pair2[0] - pair2[1]):
            return pair1
        return pair2
# @lc code=end

#
# Interview explanation
# ---------------------
# Idea:
# We need factors of either `num + 1` or `num + 2` whose difference is as small
# as possible. For a fixed number, the closest factor pair is the one nearest
# to its square root.
#
# Data structure:
# No complex structure is needed. We scan candidate divisors downward from
# `isqrt(value)` and return the first divisor that divides evenly.
#
# Walkthrough:
# 1. Define `closest_pair(value)` to find the factor pair nearest sqrt(value).
# 2. Compute that pair for `num + 1`.
# 3. Compute that pair for `num + 2`.
# 4. Return the pair with smaller absolute difference.
#
# Edge cases:
# - Prime candidate: scan falls back to `[1, value]`.
# - Perfect square: square root divides exactly, giving equal factors.
# - Tie between candidates: either is acceptable; this code returns num + 1.
#
# Complexity:
# - Time: O(sqrt(num)) in the worst case.
# - Space: O(1).
