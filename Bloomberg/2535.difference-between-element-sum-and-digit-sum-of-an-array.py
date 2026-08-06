#
# @lc app=leetcode id=2535 lang=python3
#
# [2535] Difference Between Element Sum and Digit Sum of an Array
#
# https://leetcode.com/problems/difference-between-element-sum-and-digit-sum-of-an-array/description/
#
# algorithms
# Easy (85.39%)
# Likes:    831
# Dislikes: 33
# Total Accepted:    221.1K
# Total Submissions: 258.9K
# Testcase Example:  "[1,15,6,3]"
#
# You are given a positive integer array nums.
#
#
# The element sum is the sum of all the elements in nums.
#
#
# The digit sum is the sum of all the digits (not necessarily distinct) that
# appear in nums.
#
# Return the absolute difference between the element sum and digit sum of nums.
#
# Note that the absolute difference between two integers x and y is defined as
# |x - y|.
#
#
#
# Example 1:
#
# Input: nums = [1,15,6,3]
# Output: 9
# Explanation:
# The element sum of nums is 1 + 15 + 6 + 3 = 25.
# The digit sum of nums is 1 + 1 + 5 + 6 + 3 = 16.
# The absolute difference between the element sum and digit sum is |25 - 16| =
# 9.
#
# Example 2:
#
# Input: nums = [1,2,3,4]
# Output: 0
# Explanation:
# The element sum of nums is 1 + 2 + 3 + 4 = 10.
# The digit sum of nums is 1 + 2 + 3 + 4 = 10.
# The absolute difference between the element sum and digit sum is |10 - 10| =
# 0.
#
#
#
# Constraints:
#
#
# 1 <= nums.length <= 2000
#
#
# 1 <= nums[i] <= 2000
#

# @lc code=start
from typing import List


class Solution:
    def differenceOfSum(self, nums: List[int]) -> int:
        """
        Interview explanation:
        Absolute difference between sum of elements and sum of all digits of
        elements.

        Algorithm:
        - element_sum = sum(nums); digit_sum via repeated %10 //10 per value.
        - Return abs(element_sum - digit_sum). Note element_sum >= digit_sum.

        Complexity: O(n * D) time (D digits), O(1) space.
        """
        element_sum = 0
        digit_sum = 0
        for x in nums:
            element_sum += x
            while x:
                digit_sum += x % 10
                x //= 10
        return element_sum - digit_sum

    def differenceOfSum_str(self, nums: List[int]) -> int:
        """
        Interview explanation:
        Alternate: digit sum via decimal string characters.

        Algorithm:
        - abs(sum(nums) - sum(int(d) for x in nums for d in str(x))).

        Complexity: O(n * D) time, O(D) space per conversion.
        """
        return abs(sum(nums) - sum(int(d) for x in nums for d in str(x)))
# @lc code=end
