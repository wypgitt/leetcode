#
# @lc app=leetcode id=1464 lang=python3
#
# [1464] Maximum Product of Two Elements in an Array
#
# https://leetcode.com/problems/maximum-product-of-two-elements-in-an-array/description/
#
# algorithms
# Easy (84.93%)
# Likes:    2797
# Dislikes: 243
# Total Accepted:    692K
# Total Submissions: 814K
# Testcase Example:  "[3,4,5,2]"
#
# Given the array of integers nums, you will choose two different indices i and
# j of that array. Return the maximum value of (nums[i]-1)*(nums[j]-1).
#
# Example 1:
#
# Input: nums = [3,4,5,2]
# Output: 12
# Explanation: If you choose the indices i=1 and j=2 (indexed from 0), you will
# get the maximum value, that is, (nums[1]-1)*(nums[2]-1) = (4-1)*(5-1) = 3*4 =
# 12.
#
# Example 2:
#
# Input: nums = [1,5,4,5]
# Output: 16
# Explanation: Choosing the indices i=1 and j=3 (indexed from 0), you will get
# the maximum value of (5-1)*(5-1) = 16.
#
# Example 3:
#
# Input: nums = [3,7]
# Output: 12
#
# Constraints:
#
# 2 <= nums.length <= 500
#
# 1 <= nums[i] <= 10^3
#

# @lc code=start
from typing import List


class Solution:
    def maxProduct(self, nums: List[int]) -> int:
        """
        Interview explanation:
        Maximize (a-1)*(b-1) for distinct indices — equivalent to product of
        the two largest values minus adjustments: (m1-1)*(m2-1).

        Algorithm:
        - One pass track largest and second largest; return (a-1)*(b-1).

        Complexity: O(n) time, O(1) space.
        """
        a = b = 0
        for x in nums:
            if x >= a:
                b = a
                a = x
            elif x > b:
                b = x
        return (a - 1) * (b - 1)

    def maxProduct_sort(self, nums: List[int]) -> int:
        """
        Interview explanation:
        Alternate: sort and take the last two elements.

        Algorithm:
        - Sort; (nums[-1]-1)*(nums[-2]-1).

        Complexity: O(n log n) time, O(n) space.
        """
        nums = sorted(nums)
        return (nums[-1] - 1) * (nums[-2] - 1)
# @lc code=end
