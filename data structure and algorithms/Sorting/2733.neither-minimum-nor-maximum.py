#
# @lc app=leetcode id=2733 lang=python3
#
# [2733] Neither Minimum nor Maximum
#
# https://leetcode.com/problems/neither-minimum-nor-maximum/description/
#
# algorithms
# Easy (76.51%)
# Likes:    417
# Dislikes: 20
# Total Accepted:    144.1K
# Total Submissions: 188.3K
# Testcase Example:  "[3,2,1,4]"
#
# Given an integer array nums containing distinct positive integers, find and
# return any number from the array that is neither the minimum nor the maximum
# value in the array, or -1 if there is no such number.
#
# Return the selected integer.
#
#
#
# Example 1:
#
# Input: nums = [3,2,1,4]
# Output: 2
# Explanation: In this example, the minimum value is 1 and the maximum value is
# 4. Therefore, either 2 or 3 can be valid answers.
#
# Example 2:
#
# Input: nums = [1,2]
# Output: -1
# Explanation: Since there is no number in nums that is neither the maximum nor
# the minimum, we cannot select a number that satisfies the given condition.
# Therefore, there is no answer.
#
# Example 3:
#
# Input: nums = [2,1,3]
# Output: 2
# Explanation: Since 2 is neither the maximum nor the minimum value in nums, it
# is the only valid answer.
#
#
#
# Constraints:
#
#
# 1 <= nums.length <= 100
#
#
# 1 <= nums[i] <= 100
#
#
# All values in nums are distinct
#

# @lc code=start
from typing import List


class Solution:
    def findNonMinOrMax(self, nums: List[int]) -> int:
        """
        Interview explanation:
        Return any element that is neither min nor max, or -1 if none.

        Algorithm:
        - If len < 3 return -1; else return the median of the first three elements.

        Complexity: O(1) time (or O(n) scan), O(1) space.
        """
        if len(nums) < 3:
            return -1
        a, b, c = nums[0], nums[1], nums[2]
        return a + b + c - min(a, b, c) - max(a, b, c)
# @lc code=end
