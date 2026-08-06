#
# @lc app=leetcode id=2815 lang=python3
#
# [2815] Max Pair Sum in an Array
#
# https://leetcode.com/problems/max-pair-sum-in-an-array/description/
#
# algorithms
# Easy (61.13%)
# Likes:    447
# Dislikes: 138
# Total Accepted:    63.2K
# Total Submissions: 103.3K
# Testcase Example:  "[112,131,411]"
#
#
# You are given an integer array nums. You have to find the maximum sum of
# a pair of numbers from nums such that the largest digit in both numbers
# is equal.
#
# For example, 2373 is made up of three distinct digits: 2, 3, and 7,
# where 7 is the largest among them.
#
# Return the maximum sum or -1 if no such pair exists.
#
# Example 1:
#
# Input: nums = [112,131,411]
#
# Output: -1
#
# Explanation:
#
# Each numbers largest digit in order is [2,3,4].
#
# Example 2:
#
# Input: nums = [2536,1613,3366,162]
#
# Output: 5902
#
# Explanation:
#
# All the numbers have 6 as their largest digit, so the answer is 2536 +
# 3366 = 5902.
#
# Example 3:
#
# Input: nums = [51,71,17,24,42]
#
# Output: 88
#
# Explanation:
#
# Each number's largest digit in order is [5,7,7,4,4].
#
# So we have only two possible pairs, 71 + 17 = 88 and 24 + 42 = 66.
#
# Constraints:
#
# 2 <= nums.length <= 100
#
# 1 <= nums[i] <= 10^4
#

# @lc code=start
from typing import List


class Solution:
    def maxSum(self, nums: List[int]) -> int:
        """
        Interview explanation:
        Max sum of a pair with the same largest digit; -1 if no such pair.

        Algorithm:
        - Track the max number seen for each possible max-digit 0..9.
        - For each num, update answer with num + best[d], then update best[d].

        Complexity: O(n log A) time (digits), O(1) space.
        """
        best = [-1] * 10
        ans = -1
        for x in nums:
            d = max(int(c) for c in str(x))
            if best[d] != -1:
                ans = max(ans, best[d] + x)
            best[d] = max(best[d], x)
        return ans
# @lc code=end
