#
# @lc app=leetcode id=2527 lang=python3
#
# [2527] Find Xor-Beauty of Array
#
# https://leetcode.com/problems/find-xor-beauty-of-array/description/
#
# algorithms
# Medium (71.19%)
# Likes:    400
# Dislikes: 58
# Total Accepted:    28.3K
# Total Submissions: 39.7K
# Testcase Example:  "[1,4]"
#
# You are given a 0-indexed integer array nums.
#
# The effective value of three indices i, j, and k is defined as ((nums[i] |
# nums[j]) & nums[k]).
#
# The xor-beauty of the array is the XORing of the effective values of all the
# possible triplets of indices (i, j, k) where 0 <= i, j, k < n.
#
# Return the xor-beauty of nums.
#
# Note that:
#
#
# val1 | val2 is bitwise OR of val1 and val2.
#
#
# val1 & val2 is bitwise AND of val1 and val2.
#
#
#
# Example 1:
#
# Input: nums = [1,4]
# Output: 5
# Explanation:
# The triplets and their corresponding effective values are listed below:
# - (0,0,0) with effective value ((1 | 1) & 1) = 1
# - (0,0,1) with effective value ((1 | 1) & 4) = 0
# - (0,1,0) with effective value ((1 | 4) & 1) = 1
# - (0,1,1) with effective value ((1 | 4) & 4) = 4
# - (1,0,0) with effective value ((4 | 1) & 1) = 1
# - (1,0,1) with effective value ((4 | 1) & 4) = 4
# - (1,1,0) with effective value ((4 | 4) & 1) = 0
# - (1,1,1) with effective value ((4 | 4) & 4) = 4
# Xor-beauty of array will be bitwise XOR of all beauties = 1 ^ 0 ^ 1 ^ 4 ^ 1 ^
# 4 ^ 0 ^ 4 = 5.
#
# Example 2:
#
# Input: nums = [15,45,20,2,34,35,5,44,32,30]
# Output: 34
# Explanation: The xor-beauty of the given array is 34.
#
#
#
# Constraints:
#
#
# 1 <= nums.length <= 10^5
#
#
# 1 <= nums[i] <= 10^9
#

# @lc code=start
from typing import List
from functools import reduce
import operator


class Solution:
    def xorBeauty(self, nums: List[int]) -> int:
        """
        Interview explanation:
        Xor-beauty = XOR over all (i,j,k) of ((nums[i]|nums[j]) & nums[k]).
        Bitwise linearity collapses this to the XOR of all elements.

        Algorithm:
        - Return XOR of every nums[i] (each bit contributes independently;
          all other triplet combinations cancel under XOR).

        Complexity: O(n) time, O(1) space.
        """
        return reduce(operator.xor, nums)
# @lc code=end
