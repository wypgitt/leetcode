#
# @lc app=leetcode id=665 lang=python3
#
# [665] Non-decreasing Array
#
# https://leetcode.com/problems/non-decreasing-array/description/
#
# algorithms
# Medium (25.54%)
# Likes:    5867
# Dislikes: 789
# Total Accepted:    298K
# Total Submissions: 1.2M
# Testcase Example:  "[4,2,3]"
#
# Given an array nums with n integers, your task is to check if it could become
# non-decreasing by modifying at most one element.
#
# We define an array is non-decreasing if nums[i] <= nums[i + 1] holds for
# every i (0-based) such that (0 <= i <= n - 2).
#
# Example 1:
#
# Input: nums = [4,2,3]
# Output: true
# Explanation: You could modify the first 4 to 1 to get a non-decreasing array.
#
# Example 2:
#
# Input: nums = [4,2,1]
# Output: false
# Explanation: You cannot get a non-decreasing array by modifying at most one
# element.
#
# Constraints:
#
# n == nums.length
#
# 1 <= n <= 10^4
#
# -10^5 <= nums[i] <= 10^5
#

# @lc code=start
from typing import List


class Solution:
    def checkPossibility(self, nums: List[int]) -> bool:
        """
        Interview explanation:
        At most one dip (nums[i] > nums[i+1]) may be fixed by changing either
        nums[i] or nums[i+1]. Prefer the change that preserves non-decreasing
        order with neighbors.

        Algorithm:
        - On first violation: if i==0 or nums[i-1] <= nums[i+1], set nums[i]=nums[i+1];
          else set nums[i+1]=nums[i].
        - Second violation => False.

        Complexity: O(n) time, O(1) space.
        """
        changed = False
        for i in range(len(nums) - 1):
            if nums[i] <= nums[i + 1]:
                continue
            if changed:
                return False
            changed = True
            if i == 0 or nums[i - 1] <= nums[i + 1]:
                nums[i] = nums[i + 1]
            else:
                nums[i + 1] = nums[i]
        return True
# @lc code=end
