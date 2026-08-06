#
# @lc app=leetcode id=2393 lang=python3
#
# [2393] Count Strictly Increasing Subarrays
#
# https://leetcode.com/problems/count-strictly-increasing-subarrays/description/
#
# algorithms
# Medium (70.82%)
# Likes:    143
# Dislikes: 2
# Total Accepted:    8.4K
# Total Submissions: 11.9K
# Testcase Example:  "[1,3,5,4,4,6]"
#
#
# You are given an array nums consisting of positive integers.
#
# Return the number of subarrays of nums that are in strictly increasing
# order.
#
# A subarray is a contiguous part of an array.
#
# Example 1:
#
# Input: nums = [1,3,5,4,4,6]
# Output: 10
# Explanation: The strictly increasing subarrays are the following:
# - Subarrays of length 1: [1], [3], [5], [4], [4], [6].
# - Subarrays of length 2: [1,3], [3,5], [4,6].
# - Subarrays of length 3: [1,3,5].
# The total number of subarrays is 6 + 3 + 1 = 10.
#
# Example 2:
#
# Input: nums = [1,2,3,4,5]
# Output: 15
# Explanation: Every subarray is strictly increasing. There are 15
# possible subarrays that we can take.
#
# Constraints:
#
# 1 <= nums.length <= 10^5
#
# 1 <= nums[i] <= 10^6
#
# @lc code=start

from typing import List


class Solution:
    def countSubarrays(self, nums: List[int]) -> int:
        """
        Interview explanation:
        Premium: Count contiguous subarrays that are strictly increasing.

        Algorithm:
        - For each ending index, extend streak length cnt while nums[i]>nums[i-1];
          add cnt (all suffixes of the streak ending at i).

        Complexity: O(n) time, O(1) space.
        """
        ans = cnt = 1
        for i in range(1, len(nums)):
            if nums[i - 1] < nums[i]:
                cnt += 1
            else:
                cnt = 1
            ans += cnt
        return ans

    def countSubarrays_math(self, nums: List[int]) -> int:
        """
        Interview explanation:
        Alternate: split into maximal strict runs of length L; each contributes
        L*(L+1)/2 subarrays.

        Algorithm:
        - Scan runs; accumulate triangular numbers.

        Complexity: O(n) time, O(1) space.
        """
        ans = 0
        n = len(nums)
        i = 0
        while i < n:
            j = i + 1
            while j < n and nums[j] > nums[j - 1]:
                j += 1
            L = j - i
            ans += L * (L + 1) // 2
            i = j
        return ans
# @lc code=end
