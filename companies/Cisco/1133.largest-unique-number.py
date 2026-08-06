#
# @lc app=leetcode id=1133 lang=python3
#
# [1133] Largest Unique Number
#
# https://leetcode.com/problems/largest-unique-number/description/
#
# algorithms
# Easy (71.28%)
# Likes:    357
# Dislikes: 18
# Total Accepted:    114.3K
# Total Submissions: 160.4K
# Testcase Example:  "[5,7,3,9,4,9,8,3,1]"
#
#
# Given an integer array nums, return the largest integer that only occurs
# once. If no integer occurs once, return -1.
#
# Example 1:
#
# Input: nums = [5,7,3,9,4,9,8,3,1]
# Output: 8
# Explanation: The maximum integer in the array is 9 but it is repeated.
# The number 8 occurs only once, so it is the answer.
#
# Example 2:
#
# Input: nums = [9,9,8,8]
# Output: -1
# Explanation: There is no number that occurs only once.
#
# Constraints:
#
# 1 <= nums.length <= 2000
#
# 0 <= nums[i] <= 1000
#
# @lc code=start
from typing import List
from collections import Counter


class Solution:
    def largestUniqueNumber(self, nums: List[int]) -> int:
        """
        Interview explanation:
        Premium. Return the largest integer that appears exactly once, or -1.

        Algorithm:
        - Counter; max among keys with count 1, else -1.

        Complexity: O(n) time, O(n) space.
        """
        cnt = Counter(nums)
        uniq = [x for x, c in cnt.items() if c == 1]
        return max(uniq) if uniq else -1
# @lc code=end
