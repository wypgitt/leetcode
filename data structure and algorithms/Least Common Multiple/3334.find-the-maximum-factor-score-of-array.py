#
# @lc app=leetcode id=3334 lang=python3
#
# [3334] Find the Maximum Factor Score of Array
#
# https://leetcode.com/problems/find-the-maximum-factor-score-of-array/description/
#
# algorithms
# Medium (41.38%)
# Likes:    91
# Dislikes: 13
# Total Accepted:    24.8K
# Total Submissions: 60K
# Testcase Example:  "[2,4,8,16]"
#
#
# You are given an integer array nums.
#
# The factor score of an array is defined as the product of the LCM and
# GCD of all elements of that array.
#
# Return the maximum factor score of nums after removing at most one
# element from it.
#
# Note that both the LCM and GCD of a single number are the number itself,
# and the factor score of an empty array is 0.
#
# Example 1:
#
# Input: nums = [2,4,8,16]
#
# Output: 64
#
# Explanation:
#
# On removing 2, the GCD of the rest of the elements is 4 while the LCM is
# 16, which gives a maximum factor score of 4 * 16 = 64.
#
# Example 2:
#
# Input: nums = [1,2,3,4,5]
#
# Output: 60
#
# Explanation:
#
# The maximum factor score of 60 can be obtained without removing any
# elements.
#
# Example 3:
#
# Input: nums = [3]
#
# Output: 9
#
# Constraints:
#
# 1 <= nums.length <= 100
#
# 1 <= nums[i] <= 30
#

# @lc code=start

from math import gcd
from typing import List


class Solution:
    def maxScore(self, nums: List[int]) -> int:
        """
        Interview explanation:
        Factor score = LCM * GCD of the multiset. Maximize after removing at
        most one element (or none).

        Algorithm:
        - Try the full array, then each single-element deletion.
        - Compute GCD/LCM via linear scan; lcm(a,b)=a//gcd*b.

        Complexity: O(n^2) time, O(1) extra space (n <= 100).
        """
        def score(arr: List[int]) -> int:
            if not arr:
                return 0
            g = arr[0]
            l = arr[0]
            for v in arr[1:]:
                g = gcd(g, v)
                l = l // gcd(l, v) * v
            return g * l

        ans = score(nums)
        for i in range(len(nums)):
            ans = max(ans, score(nums[:i] + nums[i + 1 :]))
        return ans
# @lc code=end

