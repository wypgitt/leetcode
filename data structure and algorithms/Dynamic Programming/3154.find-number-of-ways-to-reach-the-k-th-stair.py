#
# @lc app=leetcode id=3154 lang=python3
#
# [3154] Find Number of Ways to Reach the K-th Stair
#
# https://leetcode.com/problems/find-number-of-ways-to-reach-the-k-th-stair/description/
#
# algorithms
# Hard (37.66%)
# Likes:    206
# Dislikes: 14
# Total Accepted:    16.6K
# Total Submissions: 44.1K
# Testcase Example:  "0"
#
#
# You are given a non-negative integer k. There exists a staircase with an
# infinite number of stairs, with the lowest stair numbered 0.
#
# Alice has an integer jump, with an initial value of 0. She starts on
# stair 1 and wants to reach stair k using any number of operations. If
# she is on stair i, in one operation she can:
#
# Go down to stair i - 1. This operation cannot be used consecutively or
# on stair 0.
#
# Go up to stair i + 2^jump. And then, jump becomes jump + 1.
#
# Return the total number of ways Alice can reach stair k.
#
# Note that it is possible that Alice reaches the stair k, and performs
# some operations to reach the stair k again.
#
# Example 1:
#
# Input: k = 0
#
# Output: 2
#
# Explanation:
#
# The 2 possible ways of reaching stair 0 are:
#
# Alice starts at stair 1.
#
# Using an operation of the first type, she goes down 1 stair to reach
# stair 0.
#
# Alice starts at stair 1.
#
# Using an operation of the first type, she goes down 1 stair to reach
# stair 0.
#
# Using an operation of the second type, she goes up 2^0 stairs to reach
# stair 1.
#
# Using an operation of the first type, she goes down 1 stair to reach
# stair 0.
#
# Example 2:
#
# Input: k = 1
#
# Output: 4
#
# Explanation:
#
# The 4 possible ways of reaching stair 1 are:
#
# Alice starts at stair 1. Alice is at stair 1.
#
# Alice starts at stair 1.
#
# Using an operation of the first type, she goes down 1 stair to reach
# stair 0.
#
# Using an operation of the second type, she goes up 2^0 stairs to reach
# stair 1.
#
# Alice starts at stair 1.
#
# Using an operation of the second type, she goes up 2^0 stairs to reach
# stair 2.
#
# Using an operation of the first type, she goes down 1 stair to reach
# stair 1.
#
# Alice starts at stair 1.
#
# Using an operation of the first type, she goes down 1 stair to reach
# stair 0.
#
# Using an operation of the second type, she goes up 2^0 stairs to reach
# stair 1.
#
# Using an operation of the first type, she goes down 1 stair to reach
# stair 0.
#
# Using an operation of the second type, she goes up 2^1 stairs to reach
# stair 2.
#
# Using an operation of the first type, she goes down 1 stair to reach
# stair 1.
#
# Constraints:
#
# 0 <= k <= 10^9
#

# @lc code=start
from math import comb


class Solution:
    def waysToReachStair(self, k: int) -> int:
        """
        Interview explanation:
        Start at 1. Ups use jump sizes 2^0, 2^1, ... in order; downs subtract 1
        and cannot be consecutive. Count sequences that land on k (k up to 1e9).

        Algorithm:
        - With exactly j ups, position = 2^j - downs (start 1 + (2^j-1) - downs).
        - Need downs d = 2^j - k with 0 <= d <= j+1 (place among j+1 slots).
        - Add C(j+1, d) for each feasible j (j is tiny: 2^j ≈ k).

        Complexity: O(B) time with B≈40, O(1) space.
        """
        ans = 0
        for j in range(0, 40):
            d = (1 << j) - k
            if 0 <= d <= j + 1:
                ans += comb(j + 1, d)
        return ans
# @lc code=end
