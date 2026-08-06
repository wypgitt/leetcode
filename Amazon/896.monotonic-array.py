#
# @lc app=leetcode id=896 lang=python3
#
# [896] Monotonic Array
#
# https://leetcode.com/problems/monotonic-array/description/
#
# algorithms
# Easy (62.54%)
# Likes:    3305
# Dislikes: 107
# Total Accepted:    601K
# Total Submissions: 962K
# Testcase Example:  "[1,2,2,3]"
#
# An array is monotonic if it is either monotone increasing or monotone
# decreasing.
#
# An array nums is monotone increasing if for all i <= j, nums[i] <= nums[j].
# An array nums is monotone decreasing if for all i <= j, nums[i] >= nums[j].
#
# Given an integer array nums, return true if the given array is monotonic, or
# false otherwise.
#
# Example 1:
#
# Input: nums = [1,2,2,3]
# Output: true
#
# Example 2:
#
# Input: nums = [6,5,4,4]
# Output: true
#
# Example 3:
#
# Input: nums = [1,3,2]
# Output: false
#
# Constraints:
#
# 1 <= nums.length <= 10^5
#
# -10^5 <= nums[i] <= 10^5
#

# @lc code=start
from typing import List


class Solution:
    def isMonotonic(self, nums: List[int]) -> bool:
        """
        Interview explanation:
        Array is monotone non-increasing or non-decreasing. Track both flags
        in one pass; reject if both violated.

        Algorithm:
        - inc=dec=True; for adjacent pairs update flags; return inc or dec.

        Complexity: O(n) time, O(1) space.
        """
        inc = dec = True
        for i in range(1, len(nums)):
            if nums[i] < nums[i - 1]:
                inc = False
            if nums[i] > nums[i - 1]:
                dec = False
        return inc or dec

    def isMonotonic_sorted(self, nums: List[int]) -> bool:
        """
        Interview explanation:
        Alternate: compare to sorted ascending and reverse sorted.

        Algorithm:
        - return nums == sorted(nums) or nums == sorted(nums, reverse=True).

        Complexity: O(n log n) time, O(n) space.
        """
        return nums == sorted(nums) or nums == sorted(nums, reverse=True)
# @lc code=end

