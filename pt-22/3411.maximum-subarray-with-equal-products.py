#
# @lc app=leetcode id=3411 lang=python3
#
# [3411] Maximum Subarray With Equal Products
#
# https://leetcode.com/problems/maximum-subarray-with-equal-products/description/
#
# algorithms
# Easy (47.21%)
# Likes:    119
# Dislikes: 45
# Total Accepted:    30.8K
# Total Submissions: 65.3K
# Testcase Example:  "[1,2,1,2,1,1,1]"
#
#
# You are given an array of positive integers nums.
#
# An array arr is called product equivalent if prod(arr) == lcm(arr) *
# gcd(arr), where:
#
# prod(arr) is the product of all elements of arr.
#
# gcd(arr) is the GCD of all elements of arr.
#
# lcm(arr) is the LCM of all elements of arr.
#
# Return the length of the longest product equivalent subarray of nums.
#
# Example 1:
#
# Input: nums = [1,2,1,2,1,1,1]
#
# Output: 5
#
# Explanation:
#
# The longest product equivalent subarray is [1, 2, 1, 1, 1], where
# prod([1, 2, 1, 1, 1]) = 2, gcd([1, 2, 1, 1, 1]) = 1, and lcm([1, 2, 1,
# 1, 1]) = 2.
#
# Example 2:
#
# Input: nums = [2,3,4,5,6]
#
# Output: 3
#
# Explanation:
#
# The longest product equivalent subarray is [3, 4, 5].
#
# Example 3:
#
# Input: nums = [1,2,3,1,4,5,1]
#
# Output: 5
#
# Constraints:
#
# 2 <= nums.length <= 100
#
# 1 <= nums[i] <= 10
#

# @lc code=start
from math import gcd
from typing import List


class Solution:
    def maxLength(self, nums: List[int]) -> int:
        """
        Interview explanation:
        Longest subarray where prod == lcm * gcd. With n <= 100 and
        values <= 10, enumerate all subarrays while tracking running
        gcd/lcm/product (guard product overflow via early break).

        Algorithm:
        - For each L, expand R; maintain g, l, p.
        - lcm(a,b)=a//gcd*b; stop a window if product grows too large.
        - Track max length where p == l * g.

        Complexity: O(n^2 log A) time, O(1) extra space.
        """
        n = len(nums)
        ans = 1
        for i in range(n):
            g = l = p = nums[i]
            for j in range(i + 1, n):
                x = nums[j]
                g = gcd(g, x)
                l = l // gcd(l, x) * x
                p *= x
                if p == l * g:
                    ans = max(ans, j - i + 1)
                # values small; if product already huge vs lcm*gcd, skip
                if p > 10**18:
                    break
        return ans
# @lc code=end
