#
# @lc app=leetcode id=3099 lang=python3
#
# [3099] Harshad Number
#
# https://leetcode.com/problems/harshad-number/description/
#
# algorithms
# Easy (83.43%)
# Likes:    233
# Dislikes: 13
# Total Accepted:    122.2K
# Total Submissions: 146.5K
# Testcase Example:  "18"
#
#
# An integer divisible by the sum of its digits is said to be a Harshad
# number. You are given an integer x. Return the sum of the digits of x if
# x is a Harshad number, otherwise, return -1.
#
# Example 1:
#
# Input: x = 18
#
# Output: 9
#
# Explanation:
#
# The sum of digits of x is 9. 18 is divisible by 9. So 18 is a Harshad
# number and the answer is 9.
#
# Example 2:
#
# Input: x = 23
#
# Output: -1
#
# Explanation:
#
# The sum of digits of x is 5. 23 is not divisible by 5. So 23 is not a
# Harshad number and the answer is -1.
#
# Constraints:
#
# 1 <= x <= 100
#

# @lc code=start
class Solution:
    def sumOfTheDigitsOfHarshadNumber(self, x: int) -> int:
        """
        Interview explanation:
        Harshad number: x divisible by the sum of its digits. Return that digit
        sum if so, else -1.

        Algorithm:
        - Sum digits of x; return it when x % sum == 0.

        Complexity: O(log x) time, O(1) space.
        """
        s = 0
        n = x
        while n:
            s += n % 10
            n //= 10
        return s if x % s == 0 else -1
# @lc code=end
