#
# @lc app=leetcode id=2344 lang=python3
#
# [2344] Minimum Deletions to Make Array Divisible
#
# https://leetcode.com/problems/minimum-deletions-to-make-array-divisible/description/
#
# algorithms
# Hard (61.65%)
# Likes:    594
# Dislikes: 135
# Total Accepted:    50.7K
# Total Submissions: 82.3K
# Testcase Example:  "[2,3,2,4,3]\n[9,6,9,3,15]"
#
# You are given two positive integer arrays nums and numsDivide. You can delete
# any number of elements from nums.
#
# Return the minimum number of deletions such that the smallest element in nums
# divides all the elements of numsDivide. If this is not possible, return -1.
#
# Note that an integer x divides y if y % x == 0.
#
#
#
# Example 1:
#
# Input: nums = [2,3,2,4,3], numsDivide = [9,6,9,3,15]
# Output: 2
# Explanation:
# The smallest element in [2,3,2,4,3] is 2, which does not divide all the
# elements of numsDivide.
# We use 2 deletions to delete the elements in nums that are equal to 2 which
# makes nums = [3,4,3].
# The smallest element in [3,4,3] is 3, which divides all the elements of
# numsDivide.
# It can be shown that 2 is the minimum number of deletions needed.
#
# Example 2:
#
# Input: nums = [4,3,6], numsDivide = [8,2,6,10]
# Output: -1
# Explanation:
# We want the smallest element in nums to divide all the elements of numsDivide.
# There is no way to delete elements from nums to allow this.
#
#
#
# Constraints:
#
#
# 1 <= nums.length, numsDivide.length <= 10^5
#
#
# 1 <= nums[i], numsDivide[i] <= 10^9
#

# @lc code=start
from typing import List
from math import gcd
from functools import reduce


class Solution:
    def minOperations(self, nums: List[int], numsDivide: List[int]) -> int:
        """
        Interview explanation:
        Delete smallest elements from nums until every value in numsDivide is
        divisible by the smallest remaining nums element. Return deletions or -1.

        Algorithm:
        - g = gcd of all numsDivide. Need smallest x in nums that divides g.
          Deletions = count of elements < x after sorting unique path:
          sort nums, find first that divides g.

        Complexity: O(n log n + m log A) time, O(1) extra.
        """
        g = reduce(gcd, numsDivide)
        nums.sort()
        for i, x in enumerate(nums):
            if g % x == 0:
                return i
        return -1

    def minOperations_math(self, nums: List[int], numsDivide: List[int]) -> int:
        """
        Interview explanation:
        GCD + sort approach (same as primary).

        Algorithm:
        - Divisors of gcd(numsDivide); pick smallest present in nums.

        Complexity: O(n log n) time.
        """
        return self.minOperations(nums, numsDivide)
# @lc code=end
