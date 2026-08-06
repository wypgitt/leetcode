#
# @lc app=leetcode id=81 lang=python3
#
# [81] Search in Rotated Sorted Array II
#
# https://leetcode.com/problems/search-in-rotated-sorted-array-ii/description/
#
# algorithms
# Medium (40.01%)
# Likes:    9662
# Dislikes: 1125
# Total Accepted:    1.2M
# Total Submissions: 3.1M
# Testcase Example:  '[2,5,6,0,0,1,2]\n0'
#
# There is an integer array nums sorted in non-decreasing order (not
# necessarily with distinct values).
# 
# Before being passed to your function, nums is rotated at an unknown pivot
# index k (0 <= k < nums.length) such that the resulting array is [nums[k],
# nums[k+1], ..., nums[n-1], nums[0], nums[1], ..., nums[k-1]] (0-indexed). For
# example, [0,1,2,4,4,4,5,6,6,7] might be rotated at pivot index 5 and become
# [4,5,6,6,7,0,1,2,4,4].
# 
# Given the array nums after the rotation and an integer target, return true if
# target is in nums, or false if it is not in nums.
# 
# You must decrease the overall operation steps as much as possible.
# 
# 
# Example 1:
# Input: nums = [2,5,6,0,0,1,2], target = 0
# Output: true
# Example 2:
# Input: nums = [2,5,6,0,0,1,2], target = 3
# Output: false
# 
# 
# Constraints:
# 
# 
# 1 <= nums.length <= 5000
# -10^4 <= nums[i] <= 10^4
# nums is guaranteed to be rotated at some pivot.
# -10^4 <= target <= 10^4
# 
# 
# 
# Follow up: This problem is similar to Search in Rotated Sorted Array, but
# nums may contain duplicates. Would this affect the runtime complexity? How
# and why?
# 
#

# @lc code=start
from typing import List, Optional
class Solution:
    def search(self, nums: List[int], target: int) -> bool:
        """
        Interview explanation:
        This is rotated binary search with duplicates. Duplicates can make it
        impossible to tell which half is sorted when nums[left] == nums[mid] ==
        nums[right], so shrink both ends in that ambiguous case. Otherwise use
        the same sorted-half logic as the no-duplicate version.

        Edge cases and tests:
        - All duplicates not equal to target degrades to O(n).
        - Target at either boundary.
        - Rotated and unrotated arrays both work.

        Complexity: average O(log n), worst-case O(n) with many duplicates, O(1)
        space.
        """
        left, right = 0, len(nums) - 1
        while left <= right:
            mid = (left + right) // 2
            if nums[mid] == target:
                return True
            if nums[left] == nums[mid] == nums[right]:
                left += 1
                right -= 1
            elif nums[left] <= nums[mid]:
                if nums[left] <= target < nums[mid]:
                    right = mid - 1
                else:
                    left = mid + 1
            else:
                if nums[mid] < target <= nums[right]:
                    left = mid + 1
                else:
                    right = mid - 1
        return False
# @lc code=end


