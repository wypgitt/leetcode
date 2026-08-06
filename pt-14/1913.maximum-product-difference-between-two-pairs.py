#
# @lc app=leetcode id=1913 lang=python3
#
# [1913] Maximum Product Difference Between Two Pairs
#
# https://leetcode.com/problems/maximum-product-difference-between-two-pairs/description/
#
# algorithms
# Easy (83.09%)
# Likes:    1599
# Dislikes: 70
# Total Accepted:    306K
# Total Submissions: 368K
# Testcase Example:  "[5,6,2,7,4]"
#
# The product difference between two pairs (a, b) and (c, d) is defined as (a *
# b) - (c * d).
#
# For example, the product difference between (5, 6) and (2, 7) is (5 * 6) - (2
# * 7) = 16.
#
# Given an integer array nums, choose four distinct indices w, x, y, and z such
# that the product difference between pairs (nums[w], nums[x]) and (nums[y],
# nums[z]) is maximized.
#
# Return the maximum such product difference.
#
# Example 1:
#
# Input: nums = [5,6,2,7,4]
# Output: 34
# Explanation: We can choose indices 1 and 3 for the first pair (6, 7) and
# indices 2 and 4 for the second pair (2, 4).
# The product difference is (6 * 7) - (2 * 4) = 34.
#
# Example 2:
#
# Input: nums = [4,2,5,9,7,4,8]
# Output: 64
# Explanation: We can choose indices 3 and 6 for the first pair (9, 8) and
# indices 1 and 5 for the second pair (2, 4).
# The product difference is (9 * 8) - (2 * 4) = 64.
#
# Constraints:
#
# 4 <= nums.length <= 10^4
#
# 1 <= nums[i] <= 10^4
#

# @lc code=start
from typing import List


class Solution:
    def maxProductDifference(self, nums: List[int]) -> int:
        """
        Interview explanation:
        Max (a*b - c*d) over distinct indices = max1*max2 - min1*min2.

        Algorithm:
        - Track two largest and two smallest in one pass (or sort).

        Complexity: O(n) time, O(1) space.
        """
        max1 = max2 = float("-inf")
        min1 = min2 = float("inf")
        for x in nums:
            if x > max1:
                max2, max1 = max1, x
            elif x > max2:
                max2 = x
            if x < min1:
                min2, min1 = min1, x
            elif x < min2:
                min2 = x
        return max1 * max2 - min1 * min2

    def maxProductDifference_sort(self, nums: List[int]) -> int:
        """
        Interview explanation:
        Classic alternate: sort; ends give extremes.

        Algorithm:
        - Sort; return nums[-1]*nums[-2] - nums[0]*nums[1].

        Complexity: O(n log n) time, O(n) space.
        """
        a = sorted(nums)
        return a[-1] * a[-2] - a[0] * a[1]
# @lc code=end
