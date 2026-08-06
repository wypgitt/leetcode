#
# @lc app=leetcode id=2401 lang=python3
#
# [2401] Longest Nice Subarray
#
# https://leetcode.com/problems/longest-nice-subarray/description/
#
# algorithms
# Medium (64.78%)
# Likes:    2113
# Dislikes: 63
# Total Accepted:    180.3K
# Total Submissions: 278.3K
# Testcase Example:  "[1,3,8,48,10]"
#
# You are given an array nums consisting of positive integers.
#
# We call a subarray of nums nice if the bitwise AND of every pair of elements
# that are in different positions in the subarray is equal to 0.
#
# Return the length of the longest nice subarray.
#
# A subarray is a contiguous part of an array.
#
# Note that subarrays of length 1 are always considered nice.
#
#
#
# Example 1:
#
# Input: nums = [1,3,8,48,10]
# Output: 3
# Explanation: The longest nice subarray is [3,8,48]. This subarray satisfies
# the conditions:
# - 3 AND 8 = 0.
# - 3 AND 48 = 0.
# - 8 AND 48 = 0.
# It can be proven that no longer nice subarray can be obtained, so we return 3.
#
# Example 2:
#
# Input: nums = [3,1,5,11,13]
# Output: 1
# Explanation: The length of the longest nice subarray is 1. Any subarray of
# length 1 can be chosen.
#
#
#
# Constraints:
#
#
# 1 <= nums.length <= 10^5
#
#
# 1 <= nums[i] <= 10^9
#

# @lc code=start
from typing import List


class Solution:
    def longestNiceSubarray(self, nums: List[int]) -> int:
        """
        Interview explanation:
        A subarray is nice iff every pair has bitwise AND 0 (no shared set bits).
        Find the longest nice subarray.

        Algorithm:
        - Sliding window: maintain OR of window; when nums[r] shares bits with OR,
          shrink left until clear; track max length.

        Complexity: O(n) time, O(1) space.
        """
        ans = used = left = 0
        for right, x in enumerate(nums):
            while used & x:
                used ^= nums[left]
                left += 1
            used |= x
            ans = max(ans, right - left + 1)
        return ans

    def longestNiceSubarray_bit(self, nums: List[int]) -> int:
        """
        Interview explanation:
        Alternate: same two-pointer window expressed with explicit bit clearing.

        Algorithm:
        - Expand right; while conflict, remove nums[left] bits and advance left.

        Complexity: O(n) time, O(1) space.
        """
        ans = mask = l = 0
        for r in range(len(nums)):
            while mask & nums[r]:
                mask &= ~nums[l]
                l += 1
            mask |= nums[r]
            ans = max(ans, r - l + 1)
        return ans
# @lc code=end
