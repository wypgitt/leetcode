#
# @lc app=leetcode id=2221 lang=python3
#
# [2221] Find Triangular Sum of an Array
#
# https://leetcode.com/problems/find-triangular-sum-of-an-array/description/
#
# algorithms
# Medium (81.95%)
# Likes:    1558
# Dislikes: 77
# Total Accepted:    245.6K
# Total Submissions: 299.7K
# Testcase Example:  "[1,2,3,4,5]"
#
# You are given a 0-indexed integer array nums, where nums[i] is a digit between
# 0 and 9 (inclusive).
#
# The triangular sum of nums is the value of the only element present in nums
# after the following process terminates:
#
#
# Let nums comprise of n elements. If n == 1, end the process. Otherwise, create
# a new 0-indexed integer array newNums of length n - 1.
#
#
# For each index i, where 0 <= i < n - 1, assign the value of newNums[i] as
# (nums[i] + nums[i+1]) % 10, where % denotes modulo operator.
#
#
# Replace the array nums with newNums.
#
#
# Repeat the entire process starting from step 1.
#
# Return the triangular sum of nums.
#
#
#
# Example 1:
#
# Input: nums = [1,2,3,4,5]
# Output: 8
# Explanation:
# The above diagram depicts the process from which we obtain the triangular sum
# of the array.
#
# Example 2:
#
# Input: nums = [5]
# Output: 5
# Explanation:
# Since there is only one element in nums, the triangular sum is the value of
# that element itself.
#
#
#
# Constraints:
#
#
# 1 <= nums.length <= 1000
#
#
# 0 <= nums[i] <= 9
#

# @lc code=start
from typing import List


class Solution:
    def triangularSum(self, nums: List[int]) -> int:
        """
        Interview explanation:
        Repeatedly replace nums with adjacent pairwise sums mod 10 until one
        element remains; return it.

        Algorithm:
        - Simulate in-place shrinking, or use binomial coefficients:
          result = sum(nums[i]*C(n-1,i)) mod 10.

        Complexity: O(n^2) time, O(1) extra space (sim).
        """
        n = len(nums)
        a = nums[:]
        for length in range(n, 1, -1):
            for i in range(length - 1):
                a[i] = (a[i] + a[i + 1]) % 10
        return a[0]

    def triangularSum_math(self, nums: List[int]) -> int:
        """
        Interview explanation:
        Alternate: each nums[i] contributes C(n-1,i) times; sum mod 10.

        Algorithm:
        - Compute binomial row mod 10 carefully (or exact then %10 since n<=1000
          use exact Python ints).

        Complexity: O(n) time with running binomial, O(1) space.
        """
        n = len(nums)
        # C(n-1, i) via multiplicative formula
        ans = 0
        c = 1
        for i, x in enumerate(nums):
            ans = (ans + x * c) % 10
            # c = C(n-1, i) -> C(n-1, i+1)
            c = c * (n - 1 - i) // (i + 1) if i + 1 < n else 0
        # Note: intermediate c may not be divisible in order if we %10 early;
        # use exact int then mod at add — Python int OK; division exact for binomials.
        return ans % 10
# @lc code=end
