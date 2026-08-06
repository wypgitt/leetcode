#
# @lc app=leetcode id=2495 lang=python3
#
# [2495] Number of Subarrays Having Even Product
#
# https://leetcode.com/problems/number-of-subarrays-having-even-product/description/
#
# algorithms
# Medium (63.53%)
# Likes:    54
# Dislikes: 5
# Total Accepted:    2.9K
# Total Submissions: 4.6K
# Testcase Example:  "[9,6,7,13]"
#
#
# Given a 0-indexed integer array nums, return the number of subarrays of
# nums having an even product.
#
# Example 1:
#
# Input: nums = [9,6,7,13]
# Output: 6
# Explanation: There are 6 subarrays with an even product:
# - nums[0..1] = 9 * 6 = 54.
# - nums[0..2] = 9 * 6 * 7 = 378.
# - nums[0..3] = 9 * 6 * 7 * 13 = 4914.
# - nums[1..1] = 6.
# - nums[1..2] = 6 * 7 = 42.
# - nums[1..3] = 6 * 7 * 13 = 546.
#
# Example 2:
#
# Input: nums = [7,3,5]
# Output: 0
# Explanation: There are no subarrays with an even product.
#
# Constraints:
#
# 1 <= nums.length <= 10^5
#
# 1 <= nums[i] <= 10^5
#
# @lc code=start
from typing import List


class Solution:
    def evenProduct(self, nums: List[int]) -> int:
        """
        Interview explanation:
        Premium. Count subarrays whose product is even (contain at least one
        even element).

        Algorithm:
        - For each end i, if last even index is L, contribute L+1 subarrays.

        Complexity: O(n) time, O(1) space.
        """
        ans, last = 0, -1
        for i, v in enumerate(nums):
            if v % 2 == 0:
                last = i
            ans += last + 1
        return ans

    def evenProduct_math(self, nums: List[int]) -> int:
        """
        Interview explanation:
        Alternate: total subarrays minus all-odd subarrays.

        Algorithm:
        - Sum C(len,2)+len over maximal odd runs; subtract from n*(n+1)/2.

        Complexity: O(n) time, O(1) space.
        """
        n = len(nums)
        total = n * (n + 1) // 2
        odd = 0
        run = 0
        for v in nums:
            if v % 2:
                run += 1
            else:
                odd += run * (run + 1) // 2
                run = 0
        odd += run * (run + 1) // 2
        return total - odd
# @lc code=end

