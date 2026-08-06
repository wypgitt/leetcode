#
# @lc app=leetcode id=1909 lang=python3
#
# [1909] Remove One Element to Make the Array Strictly Increasing
#
# https://leetcode.com/problems/remove-one-element-to-make-the-array-strictly-increasing/description/
#
# algorithms
# Easy (30.53%)
# Likes:    1326
# Dislikes: 350
# Total Accepted:    91.2K
# Total Submissions: 299K
# Testcase Example:  "[1,2,10,5,7]"
#
# Given a 0-indexed integer array nums, return true if it can be made strictly
# increasing after removing exactly one element, or false otherwise. If the
# array is already strictly increasing, return true.
#
# The array nums is strictly increasing if nums[i - 1] < nums[i] for each index
# (1 <= i < nums.length).
#
# Example 1:
#
# Input: nums = [1,2,10,5,7]
# Output: true
# Explanation: By removing 10 at index 2 from nums, it becomes [1,2,5,7].
# [1,2,5,7] is strictly increasing, so return true.
#
# Example 2:
#
# Input: nums = [2,3,1,2]
# Output: false
# Explanation:
# [3,1,2] is the result of removing the element at index 0.
# [2,1,2] is the result of removing the element at index 1.
# [2,3,2] is the result of removing the element at index 2.
# [2,3,1] is the result of removing the element at index 3.
# No resulting array is strictly increasing, so return false.
#
# Example 3:
#
# Input: nums = [1,1,1]
# Output: false
# Explanation: The result of removing any element is [1,1].
# [1,1] is not strictly increasing, so return false.
#
# Constraints:
#
# 2 <= nums.length <= 1000
#
# 1 <= nums[i] <= 1000
#

# @lc code=start
from typing import List


class Solution:
    def canBeIncreasing(self, nums: List[int]) -> bool:
        """
        Interview explanation:
        Check if removing at most one element yields a strictly increasing array.
        Find first violation; try removing either of the two conflicting elements.

        Algorithm:
        - Scan for nums[i] <= nums[i-1]. Try skip i or skip i-1; verify rest.
          Allow at most one removal.

        Complexity: O(n) time, O(1) space.
        """
        def check(skip: int) -> bool:
            prev = None
            for i, x in enumerate(nums):
                if i == skip:
                    continue
                if prev is not None and x <= prev:
                    return False
                prev = x
            return True

        for i in range(1, len(nums)):
            if nums[i] <= nums[i - 1]:
                return check(i) or check(i - 1)
        return True
# @lc code=end
