#
# @lc app=leetcode id=1822 lang=python3
#
# [1822] Sign of the Product of an Array
#
# https://leetcode.com/problems/sign-of-the-product-of-an-array/description/
#
# algorithms
# Easy (64.71%)
# Likes:    2310
# Dislikes: 233
# Total Accepted:    457K
# Total Submissions: 706K
# Testcase Example:  "[-1,-2,-3,-4,3,2,1]"
#
# Implement a function signFunc(x) that returns:
#
# 1 if x is positive.
#
# -1 if x is negative.
#
# 0 if x is equal to 0.
#
# You are given an integer array nums. Let product be the product of all values
# in the array nums.
#
# Return signFunc(product).
#
# Example 1:
#
# Input: nums = [-1,-2,-3,-4,3,2,1]
# Output: 1
# Explanation: The product of all values in the array is 144, and signFunc(144)
# = 1
#
# Example 2:
#
# Input: nums = [1,5,0,2,-3]
# Output: 0
# Explanation: The product of all values in the array is 0, and signFunc(0) = 0
#
# Example 3:
#
# Input: nums = [-1,1,-1,1,-1]
# Output: -1
# Explanation: The product of all values in the array is -1, and signFunc(-1) =
# -1
#
# Constraints:
#
# 1 <= nums.length <= 1000
#
# -100 <= nums[i] <= 100
#

# @lc code=start
from typing import List


class Solution:
    def arraySign(self, nums: List[int]) -> int:
        """
        Interview explanation:
        Sign of product: 0 if any zero; else (-1)^(count of negatives).

        Algorithm (count signs):
        - Track sign; on 0 return 0; on negative flip.

        Complexity: O(n) time, O(1) space.
        """
        sign = 1
        for x in nums:
            if x == 0:
                return 0
            if x < 0:
                sign = -sign
        return sign
# @lc code=end
