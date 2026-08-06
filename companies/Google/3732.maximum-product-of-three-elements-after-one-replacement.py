#
# @lc app=leetcode id=3732 lang=python3
#
# [3732] Maximum Product of Three Elements After One Replacement
#
# https://leetcode.com/problems/maximum-product-of-three-elements-after-one-replacement/description/
#
# algorithms
# Medium (48.22%)
# Likes:    88
# Dislikes: 8
# Total Accepted:    34.2K
# Total Submissions: 70.8K
# Testcase Example:  "[-5,7,0]"
#
#
# You are given an integer array nums.
#
# You must replace exactly one element in the array with any integer value
# in the range [-10^5, 10^5] (inclusive).
#
# After performing this single replacement, determine the maximum possible
# product of any three elements at distinct indices from the modified
# array.
#
# Return an integer denoting the maximum product achievable.
#
# Example 1:
#
# Input: nums = [-5,7,0]
#
# Output: 3500000
#
# Explanation:
#
# Replacing 0 with -10^5 gives the array [-5, 7, -10^5], which has a
# product (-5) * 7 * (-10^5) = 3500000. The maximum product is 3500000.
#
# Example 2:
#
# Input: nums = [-4,-2,-1,-3]
#
# Output: 1200000
#
# Explanation:
#
# Two ways to achieve the maximum product include:
#
# [-4, -2, -3] → replace -2 with 10^5 → product = (-4) * 10^5 * (-3) =
# 1200000.
#
# [-4, -1, -3] → replace -1 with 10^5 → product = (-4) * 10^5 * (-3) =
# 1200000.
#
# The maximum product is 1200000.
#
# Example 3:
#
# Input: nums = [0,10,0]
#
# Output: 0
#
# Explanation:
#
# There is no way to replace an element with another integer and not have
# a 0 in the array. Hence, the product of all three elements will always
# be 0, and the maximum product is 0.
#
# Constraints:
#
# 3 <= nums.length <= 10^5
#
# -10^5 <= nums[i] <= 10^5
#

# @lc code=start
from typing import List


class Solution:
    def maxProduct(self, nums: List[int]) -> int:
        """
        Interview explanation:
        Replace one entry with ±1e5, then take the best product of three.
        Extreme product uses two extremes from the array times ±1e5.

        Algorithm:
        - Sort; candidates: two smallest * +1e5, two largest * +1e5,
          smallest * largest * -1e5.
        - Return the max of those three products.

        Complexity: O(n log n) time, O(1) extra space beyond sort.
        """
        nums.sort()
        a, b = nums[0], nums[1]
        c, d = nums[-2], nums[-1]
        x = 10**5
        return max(a * b * x, c * d * x, a * d * (-x))

    def maxProduct_linear(self, nums: List[int]) -> int:
        """
        Interview explanation:
        Alternate: track two smallest and two largest in one pass.

        Algorithm:
        - Same three candidate products without full sort.

        Complexity: O(n) time, O(1) space.
        """
        import heapq

        small = heapq.nsmallest(2, nums)
        large = heapq.nlargest(2, nums)
        a, b = small[0], small[1]
        d, c = large[0], large[1]
        x = 10**5
        return max(a * b * x, c * d * x, a * d * (-x))
# @lc code=end

