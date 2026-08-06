#
# @lc app=leetcode id=2447 lang=python3
#
# [2447] Number of Subarrays With GCD Equal to K
#
# https://leetcode.com/problems/number-of-subarrays-with-gcd-equal-to-k/description/
#
# algorithms
# Medium (53.38%)
# Likes:    478
# Dislikes: 72
# Total Accepted:    37K
# Total Submissions: 69.2K
# Testcase Example:  "[9,3,1,2,6,3]\n3"
#
# Given an integer array nums and an integer k, return the number of subarrays
# of nums where the greatest common divisor of the subarray's elements is k.
#
# A subarray is a contiguous non-empty sequence of elements within an array.
#
# The greatest common divisor of an array is the largest integer that evenly
# divides all the array elements.
#
#
#
# Example 1:
#
# Input: nums = [9,3,1,2,6,3], k = 3
# Output: 4
# Explanation: The subarrays of nums where 3 is the greatest common divisor of
# all the subarray's elements are:
# - [9,3,1,2,6,3]
# - [9,3,1,2,6,3]
# - [9,3,1,2,6,3]
# - [9,3,1,2,6,3]
#
# Example 2:
#
# Input: nums = [4], k = 7
# Output: 0
# Explanation: There are no subarrays of nums where 7 is the greatest common
# divisor of all the subarray's elements.
#
#
#
# Constraints:
#
#
# 1 <= nums.length <= 1000
#
#
# 1 <= nums[i], k <= 10^9
#

# @lc code=start
from typing import List
import math


class Solution:
    def subarrayGCD(self, nums: List[int], k: int) -> int:
        """
        Interview explanation:
        Count subarrays whose GCD equals k.

        Algorithm:
        - For each left endpoint, extend right with running GCD; count == k;
          stop early if GCD < k.

        Complexity: O(n^2 log A) time, O(1) space.
        """
        n = len(nums)
        ans = 0
        for i in range(n):
            g = 0
            for j in range(i, n):
                g = math.gcd(g, nums[j])
                if g == k:
                    ans += 1
                elif g < k:
                    break
        return ans
# @lc code=end
