#
# @lc app=leetcode id=504 lang=python3
#
# [504] Base 7
#
# https://leetcode.com/problems/base-7/description/
#
# algorithms
# Easy (55.01%)
# Likes:    898
# Dislikes: 240
# Total Accepted:    218K
# Total Submissions: 397K
# Testcase Example:  "100"
#
# Given an integer num, return a string of its base 7 representation.
#
# Example 1:
#
# Input: num = 100
# Output: "202"
#
# Example 2:
#
# Input: num = -7
# Output: "-10"
#
# Constraints:
#
# -10^7 <= num <= 10^7
#

# @lc code=start
class Solution:
    def convertToBase7(self, num: int) -> str:
        """
        Interview explanation:
        Standard base conversion: repeatedly take remainder mod 7; handle sign.

        Algorithm:
        - If num == 0: "0"
        - sign; while n: append n%7; n//=7; reverse digits; add '-'.

        Complexity: O(log |num|) time and space.
        """
        if num == 0:
            return "0"
        sign = "-" if num < 0 else ""
        n = abs(num)
        digits = []
        while n:
            digits.append(str(n % 7))
            n //= 7
        return sign + "".join(reversed(digits))
# @lc code=end
