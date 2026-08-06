#
# @lc app=leetcode id=1150 lang=python3
#
# [1150] Check If a Number Is Majority Element in a Sorted Array
#
# https://leetcode.com/problems/check-if-a-number-is-majority-element-in-a-sorted-array/description/
#
# algorithms
# Easy (59.94%)
# Likes:    481
# Dislikes: 36
# Total Accepted:    62.8K
# Total Submissions: 104.9K
# Testcase Example:  "[2,4,5,5,5,5,5,6,6]\n5"
#
#
# Given an integer array nums sorted in non-decreasing order and an
# integer target, return true if target is a majority element, or false
# otherwise.
#
# A majority element in an array nums is an element that appears more than
# nums.length / 2 times in the array.
#
# Example 1:
#
# Input: nums = [2,4,5,5,5,5,5,6,6], target = 5
# Output: true
# Explanation: The value 5 appears 5 times and the length of the array is
# 9.
# Thus, 5 is a majority element because 5 > 9/2 is true.
#
# Example 2:
#
# Input: nums = [10,100,101,101], target = 101
# Output: false
# Explanation: The value 101 appears 2 times and the length of the array
# is 4.
# Thus, 101 is not a majority element because 2 > 4/2 is false.
#
# Constraints:
#
# 1 <= nums.length <= 1000
#
# 1 <= nums[i], target <= 10^9
#
# nums is sorted in non-decreasing order.
#
# @lc code=start
from typing import List
import bisect


class Solution:
    def isMajorityElement(self, nums: List[int], target: int) -> bool:
        """
        Interview explanation:
        Premium. Sorted array; check if target appears more than n/2 times.
        Binary search for leftmost occurrence; check index + n//2.

        Algorithm (binary):
        - i = bisect_left(nums, target); return i+n//2 < n and nums[i+n//2]==target.

        Complexity: O(log n) time, O(1) space.
        """
        n = len(nums)
        i = bisect.bisect_left(nums, target)
        return i + n // 2 < n and nums[i + n // 2] == target
# @lc code=end
