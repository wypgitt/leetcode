#
# @lc app=leetcode id=1856 lang=python3
#
# [1856] Maximum Subarray Min-Product
#
# https://leetcode.com/problems/maximum-subarray-min-product/description/
#
# algorithms
# Medium (40.72%)
# Likes:    1587
# Dislikes: 146
# Total Accepted:    43.0K
# Total Submissions: 106K
# Testcase Example:  "[1,2,3,2]"
#
# The min-product of an array is equal to the minimum value in the array
# multiplied by the array's sum.
#
# For example, the array [3,2,5] (minimum value is 2) has a min-product of 2 *
# (3+2+5) = 2 * 10 = 20.
#
# Given an array of integers nums, return the maximum min-product of any
# non-empty subarray of nums. Since the answer may be large, return it modulo
# 10^9 + 7.
#
# Note that the min-product should be maximized before performing the modulo
# operation. Testcases are generated such that the maximum min-product without
# modulo will fit in a 64-bit signed integer.
#
# A subarray is a contiguous part of an array.
#
# Example 1:
#
# Input: nums = [1,2,3,2]
# Output: 14
# Explanation: The maximum min-product is achieved with the subarray [2,3,2]
# (minimum value is 2).
# 2 * (2+3+2) = 2 * 7 = 14.
#
# Example 2:
#
# Input: nums = [2,3,3,1,2]
# Output: 18
# Explanation: The maximum min-product is achieved with the subarray [3,3]
# (minimum value is 3).
# 3 * (3+3) = 3 * 6 = 18.
#
# Example 3:
#
# Input: nums = [3,1,5,6,4,2]
# Output: 60
# Explanation: The maximum min-product is achieved with the subarray [5,6,4]
# (minimum value is 4).
# 4 * (5+6+4) = 4 * 15 = 60.
#
# Constraints:
#
# 1 <= nums.length <= 10^5
#
# 1 <= nums[i] <= 10^7
#

# @lc code=start
from typing import List


class Solution:
    def maxSumMinProduct(self, nums: List[int]) -> int:
        """
        Interview explanation:
        Max over subarrays of (min * sum). For each index as the minimum of its
        maximal range, use prefix sums × nums[i].

        Algorithm (monotonic stack + prefix):
        - left/right next-strictly-smaller via increasing stack.
        - ans = max(nums[i] * (pref[right]-pref[left+1])); mod 1e9+7.

        Complexity: O(n) time/space.
        """
        MOD = 10**9 + 7
        n = len(nums)
        pref = [0] * (n + 1)
        for i, x in enumerate(nums):
            pref[i + 1] = pref[i] + x
        left = [-1] * n
        stack = []
        for i in range(n):
            while stack and nums[stack[-1]] >= nums[i]:
                stack.pop()
            left[i] = stack[-1] if stack else -1
            stack.append(i)
        right = [n] * n
        stack = []
        for i in range(n - 1, -1, -1):
            while stack and nums[stack[-1]] >= nums[i]:
                stack.pop()
            right[i] = stack[-1] if stack else n
            stack.append(i)
        ans = 0
        for i in range(n):
            ans = max(ans, nums[i] * (pref[right[i]] - pref[left[i] + 1]))
        return ans % MOD

    def maxSumMinProduct_bruteforce(self, nums: List[int]) -> int:
        """
        Interview explanation:
        Alternate: expand all subarrays tracking min and sum (O(n^2)).

        Algorithm:
        - For each L, expand R updating min/sum; track max product.

        Complexity: O(n^2) time.
        """
        MOD = 10**9 + 7
        n = len(nums)
        ans = 0
        for i in range(n):
            mn = nums[i]
            s = 0
            for j in range(i, n):
                mn = min(mn, nums[j])
                s += nums[j]
                ans = max(ans, mn * s)
        return ans % MOD
# @lc code=end
