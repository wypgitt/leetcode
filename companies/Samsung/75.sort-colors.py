#
# @lc app=leetcode id=75 lang=python3
#
# [75] Sort Colors
#
# https://leetcode.com/problems/sort-colors/description/
#
# algorithms
# Medium (69.55%)
# Likes:    21697
# Dislikes: 773
# Total Accepted:    3.7M
# Total Submissions: 5.4M
# Testcase Example:  '[2,0,2,1,1,0]'
#
# Given an array nums with n objects colored red, white, or blue, sort them
# in-place so that objects of the same color are adjacent, with the colors in
# the order red, white, and blue.
# 
# We will use the integers 0, 1, and 2 to represent the color red, white, and
# blue, respectively.
# 
# You must solve this problem without using the library's sort function.
# 
# 
# Example 1:
# 
# 
# Input: nums = [2,0,2,1,1,0]
# Output: [0,0,1,1,2,2]
# 
# 
# Example 2:
# 
# 
# Input: nums = [2,0,1]
# Output: [0,1,2]
# 
# 
# 
# Constraints:
# 
# 
# n == nums.length
# 1 <= n <= 300
# nums[i] is either 0, 1, or 2.
# 
# 
# 
# Follow up: Could you come up with a one-pass algorithm using only constant
# extra space?
# 
#

# @lc code=start
from typing import List, Optional
class Solution:
    def sortColors(self, nums: List[int]) -> None:
        """
        Do not return anything, modify nums in-place instead.

        Interview explanation:
        Dutch national flag partitioning keeps three regions: [0, low) are 0s,
        [low, mid) are 1s, and (high, end] are 2s. mid scans unknown values. A
        0 swaps into the low region, a 2 swaps into the high region, and a 1 is
        already in the middle region.

        Edge cases and tests:
        - Already sorted or reverse sorted arrays.
        - Arrays with only one color.
        - Empty array is handled by the loop condition.

        Complexity: O(n) time, O(1) space.
        """
        low = mid = 0
        high = len(nums) - 1

        while mid <= high:
            if nums[mid] == 0:
                nums[low], nums[mid] = nums[mid], nums[low]
                low += 1
                mid += 1
            elif nums[mid] == 2:
                nums[mid], nums[high] = nums[high], nums[mid]
                high -= 1
            else:
                mid += 1
# @lc code=end


