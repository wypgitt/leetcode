#
# @lc app=leetcode id=2470 lang=python3
#
# [2470] Number of Subarrays With LCM Equal to K
#
# https://leetcode.com/problems/number-of-subarrays-with-lcm-equal-to-k/description/
#
# algorithms
# Medium (46.43%)
# Likes:    392
# Dislikes: 41
# Total Accepted:    37.8K
# Total Submissions: 81.3K
# Testcase Example:  "[3,6,2,7,1]\n6"
#
# Given an integer array nums and an integer k, return the number of subarrays
# of nums where the least common multiple of the subarray's elements is k.
#
# A subarray is a contiguous non-empty sequence of elements within an array.
#
# The least common multiple of an array is the smallest positive integer that is
# divisible by all the array elements.
#
#
#
# Example 1:
#
# Input: nums = [3,6,2,7,1], k = 6
# Output: 4
# Explanation: The subarrays of nums where 6 is the least common multiple of all
# the subarray's elements are:
# - [3,6,2,7,1]
# - [3,6,2,7,1]
# - [3,6,2,7,1]
# - [3,6,2,7,1]
#
# Example 2:
#
# Input: nums = [3], k = 2
# Output: 0
# Explanation: There are no subarrays of nums where 2 is the least common
# multiple of all the subarray's elements.
#
#
#
# Constraints:
#
#
# 1 <= nums.length <= 1000
#
#
# 1 <= nums[i], k <= 1000
#

# @lc code=start
from typing import List
from math import lcm, gcd


class Solution:
    def subarrayLCM(self, nums: List[int], k: int) -> int:
        """
        Interview explanation:
        Count subarrays whose LCM equals k.

        Algorithm:
        - For each start, extend while LCM stays <= k and divides k; count ==k.
          LCM grows quickly so inner loops are short in practice / O(n log A).

        Complexity: O(n^2 log A) time, O(1) space (n<=1000).
        """
        n = len(nums)
        ans = 0
        for i in range(n):
            cur = 1
            for j in range(i, n):
                cur = lcm(cur, nums[j])
                if cur == k:
                    ans += 1
                if cur > k or k % cur != 0:
                    break
        return ans
# @lc code=end

