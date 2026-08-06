#
# @lc app=leetcode id=1655 lang=python3
#
# [1655] Distribute Repeating Integers
#
# https://leetcode.com/problems/distribute-repeating-integers/description/
#
# algorithms
# Hard (40.99%)
# Likes:    477
# Dislikes: 31
# Total Accepted:    22.5K
# Total Submissions: 54.9K
# Testcase Example:  "[1,2,3,4]"
#
# You are given an array of n integers, nums, where there are at most 50 unique
# values in the array. You are also given an array of m customer order
# quantities, quantity, where quantity[i] is the amount of integers the i^th
# customer ordered. Determine if it is possible to distribute nums such that:
#
# The i^th customer gets exactly quantity[i] integers,
#
# The integers the i^th customer gets are all equal, and
#
# Every customer is satisfied.
#
# Return true if it is possible to distribute nums according to the above
# conditions.
#
# Example 1:
#
# Input: nums = [1,2,3,4], quantity = [2]
# Output: false
# Explanation: The 0^th customer cannot be given two different integers.
#
# Example 2:
#
# Input: nums = [1,2,3,3], quantity = [2]
# Output: true
# Explanation: The 0^th customer is given [3,3]. The integers [1,2] are not
# used.
#
# Example 3:
#
# Input: nums = [1,1,2,2], quantity = [2,2]
# Output: true
# Explanation: The 0^th customer is given [1,1], and the 1st customer is given
# [2,2].
#
# Constraints:
#
# n == nums.length
#
# 1 <= n <= 10^5
#
# 1 <= nums[i] <= 1000
#
# m == quantity.length
#
# 1 <= m <= 10
#
# 1 <= quantity[i] <= 10^5
#
# There are at most 50 unique values in nums.
#

# @lc code=start
from typing import List
from collections import Counter


class Solution:
    def canDistribute(self, nums: List[int], quantity: List[int]) -> bool:
        """
        Interview explanation:
        Assign each customer a single value with enough frequency. Frequencies
        of distinct numbers are supplies; customers are demands. Bitmask DP over
        customer subsets: can we fill a subset with remaining freq multiset?

        Algorithm (bitmask DP):
        - cnt = sorted frequencies (only values that appear); m=len(quantity)<=10.
        - sum[mask] = total demand of subset; dp[mask]=True if assignable.
        - For each freq, update dp from filled masks by attaching a submask.

        Complexity: O(F * 3^m) time, O(2^m) space.
        """
        freq = sorted(Counter(nums).values(), reverse=True)
        m = len(quantity)
        # Use only the largest m frequencies (at most m distinct values needed)
        freq = freq[:m]
        full = 1 << m
        need = [0] * full
        for mask in range(1, full):
            lsb = mask & -mask
            i = lsb.bit_length() - 1
            need[mask] = need[mask ^ lsb] + quantity[i]

        dp = [False] * full
        dp[0] = True
        for f in freq:
            ndp = dp[:]
            for mask in range(full):
                if not dp[mask]:
                    continue
                # enumerate submasks of remaining customers
                remain = (full - 1) ^ mask
                sub = remain
                while sub:
                    if need[sub] <= f:
                        ndp[mask | sub] = True
                    sub = (sub - 1) & remain
            dp = ndp
            if dp[full - 1]:
                return True
        return dp[full - 1]
# @lc code=end
