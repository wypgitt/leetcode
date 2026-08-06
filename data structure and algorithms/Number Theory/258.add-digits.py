#
# @lc app=leetcode id=258 lang=python3
#
# [258] Add Digits
#
# https://leetcode.com/problems/add-digits/description/
#
# algorithms
# Easy (69.18%)
# Likes:    5584
# Dislikes: 1986
# Total Accepted:    1.3M
# Total Submissions: 1.9M
# Testcase Example:  "38"
#
# Given an integer num, repeatedly add all its digits until the result has only
# one digit, and return it.
#
# Example 1:
#
# Input: num = 38
# Output: 2
# Explanation: The process is
# 38 --> 3 + 8 --> 11
# 11 --> 1 + 1 --> 2
# Since 2 has only one digit, return it.
#
# Example 2:
#
# Input: num = 0
# Output: 0
#
# Constraints:
#
# 0 <= num <= 2^31 - 1
#
# Follow up: Could you do it without any loop/recursion in O(1) runtime?
#

# @lc code=start
class Solution:
    def addDigits(self, num: int) -> int:
        """
        Interview explanation:
        Digital root: repeatedly sum digits until one digit remains. Closed form
        is num % 9, with 0 mapping to 0 and multiples of 9 mapping to 9.

        Algorithm:
        - If num == 0: return 0; else return 1 + (num - 1) % 9 (or equiv. num % 9).

        Complexity: O(1) time, O(1) space.
        """
        if num == 0:
            return 0
        return 1 + (num - 1) % 9

    def addDigitsLoop(self, num: int) -> int:
        """
        Interview explanation:
        Naive loop: while num >= 10, replace with sum of digits.

        Algorithm:
        - Sum digits repeatedly until a single digit remains.

        Complexity: O(log num) time, O(1) space.
        """
        while num >= 10:
            total = 0
            while num:
                num, d = divmod(num, 10)
                total += d
            num = total
        return num
# @lc code=end
