#
# @lc app=leetcode id=3153 lang=python3
#
# [3153] Sum of Digit Differences of All Pairs
#
# https://leetcode.com/problems/sum-of-digit-differences-of-all-pairs/description/
#
# algorithms
# Medium (43.30%)
# Likes:    232
# Dislikes: 20
# Total Accepted:    30.4K
# Total Submissions: 70.2K
# Testcase Example:  "[13,23,12]"
#
#
# You are given an array nums consisting of positive integers where all
# integers have the same number of digits.
#
# The digit difference between two integers is the count of different
# digits that are in the same position in the two integers.
#
# Return the sum of the digit differences between all pairs of integers in
# nums.
#
# Example 1:
#
# Input: nums = [13,23,12]
#
# Output: 4
#
# Explanation:
#
# We have the following:
#
# - The digit difference between 13 and 23 is 1.
#
# - The digit difference between 13 and 12 is 1.
#
# - The digit difference between 23 and 12 is 2.
#
# So the total sum of digit differences between all pairs of integers is 1
# + 1 + 2 = 4.
#
# Example 2:
#
# Input: nums = [10,10,10,10]
#
# Output: 0
#
# Explanation:
#
# All the integers in the array are the same. So the total sum of digit
# differences between all pairs of integers will be 0.
#
# Constraints:
#
# 2 <= nums.length <= 10^5
#
# 1 <= nums[i] < 10^9
#
# All integers in nums have the same number of digits.
#

# @lc code=start
from typing import List


class Solution:
    def sumDigitDifferences(self, nums: List[int]) -> int:
        """
        Interview explanation:
        For each digit place, sum over pairs how often the digits differ.
        All numbers share the same digit length.

        Algorithm:
        - For each place, count digit frequencies; differing pairs equal
          sum_d freq[d] * (n - freq[d]) / 2.
        - Peel least-significant digits across all numbers for D places.

        Complexity: O(n * D) time with D = digits, O(n) space.
        """
        n = len(nums)
        dlen = len(str(nums[0]))
        vals = nums[:]
        ans = 0
        for _ in range(dlen):
            freq = [0] * 10
            for i, v in enumerate(vals):
                freq[v % 10] += 1
                vals[i] = v // 10
            place = 0
            for f in freq:
                place += f * (n - f)
            ans += place // 2
        return ans
# @lc code=end
