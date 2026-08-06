#
# @lc app=leetcode id=1085 lang=python3
#
# [1085] Sum of Digits in the Minimum Number
#
# https://leetcode.com/problems/sum-of-digits-in-the-minimum-number/description/
#
# algorithms
# Easy (76.73%)
# Likes:    122
# Dislikes: 151
# Total Accepted:    26.2K
# Total Submissions: 34.2K
# Testcase Example:  "[34,23,1,24,75,33,54,8]"
#
#
# Given an integer array nums, return 0 if the sum of the digits of the
# minimum integer in nums is odd, or 1 otherwise.
#
# Example 1:
#
# Input: nums = [34,23,1,24,75,33,54,8]
# Output: 0
# Explanation: The minimal element is 1, and the sum of those digits is 1
# which is odd, so the answer is 0.
#
# Example 2:
#
# Input: nums = [99,77,33,66,55]
# Output: 1
# Explanation: The minimal element is 33, and the sum of those digits is 3
# + 3 = 6 which is even, so the answer is 1.
#
# Constraints:
#
# 1 <= nums.length <= 100
#
# 1 <= nums[i] <= 100
#
# @lc code=start
from typing import List


class Solution:
    def sumOfDigits(self, nums: List[int]) -> int:
        """
        Interview explanation:
        Premium. Let S be the digit sum of min(nums). Return 0 if S is odd,
        otherwise return 1.

        Algorithm:
        - m = min(nums); sum digits; return 1 - (S % 2).

        Complexity: O(n + log M) time, O(1) space.
        """
        m = min(nums)
        s = 0
        while m:
            s += m % 10
            m //= 10
        return 0 if s % 2 else 1
# @lc code=end
