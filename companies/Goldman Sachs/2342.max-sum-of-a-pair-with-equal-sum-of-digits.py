#
# @lc app=leetcode id=2342 lang=python3
#
# [2342] Max Sum of a Pair With Equal Sum of Digits
#
# https://leetcode.com/problems/max-sum-of-a-pair-with-equal-sum-of-digits/description/
#
# algorithms
# Medium (65.93%)
# Likes:    1414
# Dislikes: 46
# Total Accepted:    253.4K
# Total Submissions: 384.4K
# Testcase Example:  "[18,43,36,13,7]"
#
# You are given a 0-indexed array nums consisting of positive integers. You can
# choose two indices i and j, such that i != j, and the sum of digits of the
# number nums[i] is equal to that of nums[j].
#
# Return the maximum value of nums[i] + nums[j] that you can obtain over all
# possible indices i and j that satisfy the conditions. If no such pair of
# indices exists, return -1.
#
#
#
# Example 1:
#
# Input: nums = [18,43,36,13,7]
# Output: 54
# Explanation: The pairs (i, j) that satisfy the conditions are:
# - (0, 2), both numbers have a sum of digits equal to 9, and their sum is 18 +
# 36 = 54.
# - (1, 4), both numbers have a sum of digits equal to 7, and their sum is 43 +
# 7 = 50.
# So the maximum sum that we can obtain is 54.
#
# Example 2:
#
# Input: nums = [10,12,19,14]
# Output: -1
# Explanation: There are no two numbers that satisfy the conditions, so we
# return -1.
#
#
#
# Constraints:
#
#
# 1 <= nums.length <= 10^5
#
#
# 1 <= nums[i] <= 10^9
#

# @lc code=start
from typing import List


class Solution:
    def maximumSum(self, nums: List[int]) -> int:
        """
        Interview explanation:
        Max sum of two nums with equal digit-sum; -1 if none.

        Algorithm:
        - Map digit_sum -> largest value seen; when colliding, update answer
          with sum and keep the larger value.

        Complexity: O(n * log A) time, O(digit_sum range) space.
        """
        best = {}
        ans = -1

        def digit_sum(x: int) -> int:
            s = 0
            while x:
                s += x % 10
                x //= 10
            return s

        for x in nums:
            s = digit_sum(x)
            if s in best:
                ans = max(ans, best[s] + x)
                best[s] = max(best[s], x)
            else:
                best[s] = x
        return ans
# @lc code=end
