#
# @lc app=leetcode id=2148 lang=python3
#
# [2148] Count Elements With Strictly Smaller and Greater Elements 
#
# https://leetcode.com/problems/count-elements-with-strictly-smaller-and-greater-elements/description/
#
# algorithms
# Easy (60.14%)
# Likes:    723
# Dislikes: 46
# Total Accepted:    86.4K
# Total Submissions: 143.7K
# Testcase Example:  "[11,7,2,15]"
#
# Given an integer array nums, return the number of elements that have both a
# strictly smaller and a strictly greater element appear in nums.
#
#
#
# Example 1:
#
# Input: nums = [11,7,2,15]
# Output: 2
# Explanation: The element 7 has the element 2 strictly smaller than it and the
# element 11 strictly greater than it.
# Element 11 has element 7 strictly smaller than it and element 15 strictly
# greater than it.
# In total there are 2 elements having both a strictly smaller and a strictly
# greater element appear in nums.
#
# Example 2:
#
# Input: nums = [-3,3,3,90]
# Output: 2
# Explanation: The element 3 has the element -3 strictly smaller than it and the
# element 90 strictly greater than it.
# Since there are two elements with the value 3, in total there are 2 elements
# having both a strictly smaller and a strictly greater element appear in nums.
#
#
#
# Constraints:
#
#
# 1 <= nums.length <= 100
#
#
# -10^5 <= nums[i] <= 10^5
#


# @lc code=start
from typing import List


class Solution:
    def countElements(self, nums: List[int]) -> int:
        """
        Interview explanation:
        Count elements that have both a strictly smaller and a strictly greater
        element somewhere in the array.

        Algorithm:
        - Count how many are not equal to global min or max (if min!=max).

        Complexity: O(n) time, O(1) space.
        """
        mn, mx = min(nums), max(nums)
        if mn == mx:
            return 0
        return sum(mn < x < mx for x in nums)
# @lc code=end

