#
# @lc app=leetcode id=2436 lang=python3
#
# [2436] Minimum Split Into Subarrays With GCD Greater Than One
#
# https://leetcode.com/problems/minimum-split-into-subarrays-with-gcd-greater-than-one/description/
#
# algorithms
# Medium (69.77%)
# Likes:    45
# Dislikes: 11
# Total Accepted:    3K
# Total Submissions: 4.3K
# Testcase Example:  "[12,6,3,14,8]"
#
#
# You are given an array nums consisting of positive integers.
#
# Split the array into one or more disjoint subarrays such that:
#
# Each element of the array belongs to exactly one subarray, and
#
# The GCD of the elements of each subarray is strictly greater than 1.
#
# Return the minimum number of subarrays that can be obtained after the
# split.
#
# Note that:
#
# The GCD of a subarray is the largest positive integer that evenly
# divides all the elements of the subarray.
#
# A subarray is a contiguous part of the array.
#
# Example 1:
#
# Input: nums = [12,6,3,14,8]
# Output: 2
# Explanation: We can split the array into the subarrays: [12,6,3] and
# [14,8].
# - The GCD of 12, 6 and 3 is 3, which is strictly greater than 1.
# - The GCD of 14 and 8 is 2, which is strictly greater than 1.
# It can be shown that splitting the array into one subarray will make the
# GCD = 1.
#
# Example 2:
#
# Input: nums = [4,12,6,14]
# Output: 1
# Explanation: We can split the array into only one subarray, which is the
# whole array.
#
# Constraints:
#
# 1 <= nums.length <= 2000
#
# 2 <= nums[i] <= 10^9
#
# @lc code=start
from typing import List
import math


class Solution:
    def minimumSplits(self, nums: List[int]) -> int:
        """
        Interview explanation:
        Premium. Split into minimum contiguous subarrays each with GCD > 1.

        Algorithm:
        - Greedy extend while running GCD > 1; otherwise start a new split.

        Complexity: O(n log A) time, O(1) space.
        """
        ans = 1
        g = nums[0]
        for x in nums[1:]:
            ng = math.gcd(g, x)
            if ng == 1:
                ans += 1
                g = x
            else:
                g = ng
        return ans
# @lc code=end
