#
# @lc app=leetcode id=3326 lang=python3
#
# [3326] Minimum Division Operations to Make Array Non Decreasing
#
# https://leetcode.com/problems/minimum-division-operations-to-make-array-non-decreasing/description/
#
# algorithms
# Medium (29.41%)
# Likes:    139
# Dislikes: 31
# Total Accepted:    24.7K
# Total Submissions: 84.1K
# Testcase Example:  "[25,7]"
#
#
# You are given an integer array nums.
#
# Any positive divisor of a natural number x that is strictly less than x
# is called a proper divisor of x. For example, 2 is a proper divisor of
# 4, while 6 is not a proper divisor of 6.
#
# You are allowed to perform an operation any number of times on nums,
# where in each operation you select any one element from nums and divide
# it by its greatest proper divisor.
#
# Return the minimum number of operations required to make the array
# non-decreasing.
#
# If it is not possible to make the array non-decreasing using any number
# of operations, return -1.
#
# Example 1:
#
# Input: nums = [25,7]
#
# Output: 1
#
# Explanation:
#
# Using a single operation, 25 gets divided by 5 and nums becomes [5, 7].
#
# Example 2:
#
# Input: nums = [7,7,6]
#
# Output: -1
#
# Example 3:
#
# Input: nums = [1,1,1,1]
#
# Output: 0
#
# Constraints:
#
# 1 <= nums.length <= 10^5
#
# 1 <= nums[i] <= 10^6
#

# @lc code=start

from math import isqrt
from typing import List


class Solution:
    def minOperations(self, nums: List[int]) -> int:
        """
        Interview explanation:
        One division by the greatest proper divisor replaces x with its smallest
        prime factor. At most one useful op per index; greedily fix RTL.

        Algorithm:
        - Walk i from n-2 down to 0. If nums[i] > nums[i+1], replace with SPF;
          if SPF still too large (prime too big), return -1; else count 1 op.
        - Leaving a larger feasible value helps the left side.

        Complexity: O(n sqrt M) time, O(1) space (M = max nums).
        """
        def spf(num: int) -> int:
            for d in range(2, isqrt(num) + 1):
                if num % d == 0:
                    return d
            return num

        ans = 0
        for i in range(len(nums) - 2, -1, -1):
            if nums[i] > nums[i + 1]:
                p = spf(nums[i])
                if p > nums[i + 1]:
                    return -1
                nums[i] = p
                ans += 1
        return ans
# @lc code=end

