#
# @lc app=leetcode id=1295 lang=python3
#
# [1295] Find Numbers with Even Number of Digits
#
# https://leetcode.com/problems/find-numbers-with-even-number-of-digits/description/
#
# algorithms
# Easy (79.92%)
# Likes:    3005
# Dislikes: 151
# Total Accepted:    1.1M
# Total Submissions: 1.4M
# Testcase Example:  "[12,345,2,6,7896]"
#
# Given an array nums of integers, return how many of them contain an even
# number of digits.
#
# Example 1:
#
# Input: nums = [12,345,2,6,7896]
# Output: 2
# Explanation:
# 12 contains 2 digits (even number of digits).
# 345 contains 3 digits (odd number of digits).
# 2 contains 1 digit (odd number of digits).
# 6 contains 1 digit (odd number of digits).
# 7896 contains 4 digits (even number of digits).
# Therefore only 12 and 7896 contain an even number of digits.
#
# Example 2:
#
# Input: nums = [555,901,482,1771]
# Output: 1
# Explanation:
# Only 1771 contains an even number of digits.
#
# Constraints:
#
# 1 <= nums.length <= 500
#
# 1 <= nums[i] <= 10^5
#

# @lc code=start

from typing import List


class Solution:
    def findNumbers(self, nums: List[int]) -> int:
        """
        Interview explanation:
        Count how many numbers have an even number of digits.

        Algorithm:
        - For each num: digits = floor(log10(num))+1; count if even.
          Or via len(str(num))%2==0.

        Complexity: O(n) time, O(1) space (math) / O(log num) for str.
        """
        import math

        ans = 0
        for x in nums:
            digits = int(math.log10(x)) + 1
            if digits % 2 == 0:
                ans += 1
        return ans

    def findNumbers_str(self, nums: List[int]) -> int:
        """
        Interview explanation:
        Alternate string length check.

        Algorithm:
        - sum(len(str(x))%2==0 for x in nums)

        Complexity: O(n log A) time.
        """
        return sum(len(str(x)) % 2 == 0 for x in nums)
# @lc code=end
