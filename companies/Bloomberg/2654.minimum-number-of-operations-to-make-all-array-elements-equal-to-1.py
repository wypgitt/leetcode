#
# @lc app=leetcode id=2654 lang=python3
#
# [2654] Minimum Number of Operations to Make All Array Elements Equal to 1
#
# https://leetcode.com/problems/minimum-number-of-operations-to-make-all-array-elements-equal-to-1/description/
#
# algorithms
# Medium (54.72%)
# Likes:    792
# Dislikes: 50
# Total Accepted:    89.8K
# Total Submissions: 164.1K
# Testcase Example:  "[2,6,3,4]"
#
# You are given a 0-indexed array nums consisting of positive integers. You can
# do the following operation on the array any number of times:
#
#
# Select an index i such that 0 <= i < n - 1 and replace either of nums[i] or
# nums[i+1] with their gcd value.
#
# Return the minimum number of operations to make all elements of nums equal to
# 1. If it is impossible, return -1.
#
# The gcd of two integers is the greatest common divisor of the two integers.
#
#
#
# Example 1:
#
# Input: nums = [2,6,3,4]
# Output: 4
# Explanation: We can do the following operations:
# - Choose index i = 2 and replace nums[2] with gcd(3,4) = 1. Now we have nums =
# [2,6,1,4].
# - Choose index i = 1 and replace nums[1] with gcd(6,1) = 1. Now we have nums =
# [2,1,1,4].
# - Choose index i = 0 and replace nums[0] with gcd(2,1) = 1. Now we have nums =
# [1,1,1,4].
# - Choose index i = 2 and replace nums[3] with gcd(1,4) = 1. Now we have nums =
# [1,1,1,1].
#
# Example 2:
#
# Input: nums = [2,10,6,14]
# Output: -1
# Explanation: It can be shown that it is impossible to make all the elements
# equal to 1.
#
#
#
# Constraints:
#
#
# 2 <= nums.length <= 50
#
#
# 1 <= nums[i] <= 10^6
#

# @lc code=start

from typing import List
from math import gcd


class Solution:
    def minOperations(self, nums: List[int]) -> int:
        """
        Interview explanation:
        Replace nums[i] with gcd(nums[i], neighbor); min ops so every element becomes 1.

        Algorithm:
        - If any 1: answer = n - count(1). Else find shortest subarray with gcd 1 of length L;
          cost L-1 to create a 1 then n-1 to spread. -1 if overall gcd > 1.

        Complexity: O(n^2 log A) time, O(1) space.
        """
        n = len(nums)
        ones = sum(1 for x in nums if x == 1)
        if ones:
            return n - ones
        g = 0
        for x in nums:
            g = gcd(g, x)
        if g > 1:
            return -1
        best = n
        for i in range(n):
            cur = 0
            for j in range(i, n):
                cur = gcd(cur, nums[j])
                if cur == 1:
                    best = min(best, j - i + 1)
                    break
        return best + n - 2
# @lc code=end
