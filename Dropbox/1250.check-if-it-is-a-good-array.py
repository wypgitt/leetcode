#
# @lc app=leetcode id=1250 lang=python3
#
# [1250] Check If It Is a Good Array
#
# https://leetcode.com/problems/check-if-it-is-a-good-array/description/
#
# algorithms
# Hard (65.7%)
# Likes:    593
# Dislikes: 387
# Total Accepted:    45.1K
# Total Submissions: 68.6K
# Testcase Example:  "[12,5,7,23]"
#
# Given an array nums of positive integers. Your task is to select some subset
# of nums, multiply each element by an integer and add all these numbers. The
# array is said to be good if you can obtain a sum of 1 from the array by any
# possible subset and multiplicand.
#
# Return True if the array is good otherwise return False.
#
# Example 1:
#
# Input: nums = [12,5,7,23]
# Output: true
# Explanation: Pick numbers 5 and 7.
# 5*3 + 7*(-2) = 1
#
# Example 2:
#
# Input: nums = [29,6,10]
# Output: true
# Explanation: Pick numbers 29, 6 and 10.
# 29*1 + 6*(-3) + 10*(-1) = 1
#
# Example 3:
#
# Input: nums = [3,6]
# Output: false
#
# Constraints:
#
# 1 <= nums.length <= 10^5
#
# 1 <= nums[i] <= 10^9
#


# @lc code=start
from typing import List
from math import gcd
from functools import reduce

class Solution:
    def isGoodArray(self, nums: List[int]) -> bool:
        """
        Interview explanation:
        By Bézout's identity, integer linear combinations of nums can form 1
        iff gcd of all numbers is 1. Good array ⇔ gcd(nums)==1.

        Algorithm:
        - Reduce gcd across array; return == 1

        Complexity: O(n log A) time, O(1) space.
        """
        g = 0
        for x in nums:
            g = gcd(g, x)
            if g == 1:
                return True
        return g == 1

    def isGoodArray_reduce(self, nums: List[int]) -> bool:
        """
        Interview explanation:
        Alternate: functools.reduce(gcd, nums) == 1.

        Algorithm:
        - return reduce(gcd, nums) == 1

        Complexity: O(n log A).
        """
        return reduce(gcd, nums) == 1
# @lc code=end
