#
# @lc app=leetcode id=1134 lang=python3
#
# [1134] Armstrong Number
#
# https://leetcode.com/problems/armstrong-number/description/
#
# algorithms
# Easy (77.85%)
# Likes:    217
# Dislikes: 20
# Total Accepted:    43.2K
# Total Submissions: 55.5K
# Testcase Example:  "153"
#
#
# Given an integer n, return true if and only if it is an Armstrong
# number.
#
# The k-digit number n is an Armstrong number if and only if the k^th
# power of each digit sums to n.
#
# Example 1:
#
# Input: n = 153
# Output: true
# Explanation: 153 is a 3-digit number, and 153 = 1^3 + 5^3 + 3^3.
#
# Example 2:
#
# Input: n = 123
# Output: false
# Explanation: 123 is a 3-digit number, and 123 != 1^3 + 2^3 + 3^3 = 36.
#
# Constraints:
#
# 1 <= n <= 10^8
#
# @lc code=start
class Solution:
    def isArmstrong(self, n: int) -> bool:
        """
        Interview explanation:
        Premium. Armstrong number: sum of each digit raised to the number of
        digits equals n (e.g. 153 = 1^3+5^3+3^3).

        Algorithm:
        - k = number of digits; sum d^k for each digit; compare to n.

        Complexity: O(log n) time, O(1) space.
        """
        s = str(n)
        k = len(s)
        return sum(int(d) ** k for d in s) == n
# @lc code=end
