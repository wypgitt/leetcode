#
# @lc app=leetcode id=628 lang=python3
#
# [628] Maximum Product of Three Numbers
#
# https://leetcode.com/problems/maximum-product-of-three-numbers/description/
#
# algorithms
# Easy (48.17%)
# Likes:    4824
# Dislikes: 735
# Total Accepted:    671K
# Total Submissions: 1.4M
# Testcase Example:  "[1,2,3]"
#
# Given an integer array nums, find three numbers whose product is maximum and
# return the maximum product.
#
# Example 1:
#
# Input: nums = [1,2,3]
# Output: 6
#
# Example 2:
#
# Input: nums = [1,2,3,4]
# Output: 24
#
# Example 3:
#
# Input: nums = [-1,-2,-3]
# Output: -6
#
# Constraints:
#
# 3 <= nums.length <= 10^4
#
# -1000 <= nums[i] <= 1000
#

# @lc code=start

from typing import List


class Solution:
    def maximumProduct(self, nums: List[int]) -> int:
        """
        Interview explanation:
        Max product of 3 is either three largest positives, or two smallest
        (most negative) times the largest.

        Algorithm:
        - Track max1>=max2>=max3 and min1<=min2 in one pass (or sort).
        - Return max(max1*max2*max3, min1*min2*max1).

        Complexity: O(N) time, O(1) space.
        """
        max1 = max2 = max3 = float("-inf")
        min1 = min2 = float("inf")
        for x in nums:
            if x > max1:
                max3, max2, max1 = max2, max1, x
            elif x > max2:
                max3, max2 = max2, x
            elif x > max3:
                max3 = x
            if x < min1:
                min2, min1 = min1, x
            elif x < min2:
                min2 = x
        return max(max1 * max2 * max3, min1 * min2 * max1)
# @lc code=end
