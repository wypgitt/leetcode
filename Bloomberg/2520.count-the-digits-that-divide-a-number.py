#
# @lc app=leetcode id=2520 lang=python3
#
# [2520] Count the Digits That Divide a Number
#
# https://leetcode.com/problems/count-the-digits-that-divide-a-number/description/
#
# algorithms
# Easy (86.08%)
# Likes:    708
# Dislikes: 44
# Total Accepted:    204.6K
# Total Submissions: 237.6K
# Testcase Example:  "7"
#
# Given an integer num, return the number of digits in num that divide num.
#
# An integer val divides nums if nums % val == 0.
#
#
#
# Example 1:
#
# Input: num = 7
# Output: 1
# Explanation: 7 divides itself, hence the answer is 1.
#
# Example 2:
#
# Input: num = 121
# Output: 2
# Explanation: 121 is divisible by 1, but not 2. Since 1 occurs twice as a
# digit, we return 2.
#
# Example 3:
#
# Input: num = 1248
# Output: 4
# Explanation: 1248 is divisible by all of its digits, hence the answer is 4.
#
#
#
# Constraints:
#
#
# 1 <= num <= 10^9
#
#
# num does not contain 0 as one of its digits.
#

# @lc code=start
class Solution:
    def countDigits(self, num: int) -> int:
        """
        Interview explanation:
        Count how many digits of num divide num (no zero digits in constraints).

        Algorithm:
        - Peel digits via %10 / //10; count those with num % d == 0.

        Complexity: O(log num) time, O(1) space.
        """
        ans = 0
        x = num
        while x:
            d = x % 10
            if num % d == 0:
                ans += 1
            x //= 10
        return ans

    def countDigits_math(self, num: int) -> int:
        """
        Interview explanation:
        Same digit-divides check via string digits.

        Algorithm:
        - For each char digit, int(d) and test num % d == 0.

        Complexity: O(log num) time, O(log num) space for string.
        """
        return sum(1 for ch in str(num) if num % int(ch) == 0)
# @lc code=end
