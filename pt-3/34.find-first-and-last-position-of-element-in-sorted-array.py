#
# @lc app=leetcode id=34 lang=python3
#
# [34] Find First and Last Position of Element in Sorted Array
#
# https://leetcode.com/problems/find-first-and-last-position-of-element-in-sorted-array/description/
#
# algorithms
# Medium (48.81%)
# Likes:    23361
# Dislikes: 654
# Total Accepted:    3.3M
# Total Submissions: 6.8M
# Testcase Example:  '[5,7,7,8,8,10]\n8'
#
# Given an array of integers nums sorted in non-decreasing order, find the
# starting and ending position of a given target value.
# 
# If target is not found in the array, return [-1, -1].
# 
# You must write an algorithm with O(log n) runtime complexity.
# 
# 
# Example 1:
# Input: nums = [5,7,7,8,8,10], target = 8
# Output: [3,4]
# Example 2:
# Input: nums = [5,7,7,8,8,10], target = 6
# Output: [-1,-1]
# Example 3:
# Input: nums = [], target = 0
# Output: [-1,-1]
# 
# 
# Constraints:
# 
# 
# 0 <= nums.length <= 10^5
# -10^9 <= nums[i] <= 10^9
# nums is a non-decreasing array.
# -10^9 <= target <= 10^9
# 
# 
#

# @lc code=start
from typing import List, Optional
class Solution:
    def searchRange(self, nums: List[int], target: int) -> List[int]:
        """
        Interview explanation:
        Since the array is sorted, the first and last positions are boundaries.
        Use binary search twice: lower_bound(target) gives the first index with
        value >= target, and lower_bound(target + 1) - 1 gives the last index
        with value == target.

        Edge cases and tests:
        - Empty array returns [-1, -1].
        - Target absent after lower_bound validation returns [-1, -1].
        - All elements equal target returns [0, n-1].

        Complexity: O(log n) time, O(1) space.
        """
        def lower_bound(value: int) -> int:
            left, right = 0, len(nums)
            while left < right:
                mid = (left + right) // 2
                if nums[mid] < value:
                    left = mid + 1
                else:
                    right = mid
            return left

        first = lower_bound(target)
        if first == len(nums) or nums[first] != target:
            return [-1, -1]
        return [first, lower_bound(target + 1) - 1]
# @lc code=end


