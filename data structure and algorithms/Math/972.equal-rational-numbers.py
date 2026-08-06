#
# @lc app=leetcode id=972 lang=python3
#
# [972] Equal Rational Numbers
#
# https://leetcode.com/problems/equal-rational-numbers/description/
#
# algorithms
# Hard (46.52%)
# Likes:    107
# Dislikes: 218
# Total Accepted:    10.5K
# Total Submissions: 22.6K
# Testcase Example:  "\"0.(52)\""
#
# Given two strings s and t, each of which represents a non-negative rational
# number, return true if and only if they represent the same number. The
# strings may use parentheses to denote the repeating part of the rational
# number.
#
# A rational number can be represented using up to three parts: <IntegerPart>,
# <NonRepeatingPart>, and a <RepeatingPart>. The number will be represented in
# one of the following three ways:
#
# <IntegerPart>
#
# For example, 12, 0, and 123.
#
# <IntegerPart><.><NonRepeatingPart>
#
# For example, 0.5, 1., 2.12, and 123.0001.
#
# <IntegerPart><.><NonRepeatingPart><(><RepeatingPart><)>
#
# For example, 0.1(6), 1.(9), 123.00(1212).
#
# The repeating portion of a decimal expansion is conventionally denoted within
# a pair of round brackets. For example:
#
# 1/6 = 0.16666666... = 0.1(6) = 0.1666(6) = 0.166(66).
#
# Example 1:
#
# Input: s = "0.(52)", t = "0.5(25)"
# Output: true
# Explanation: Because "0.(52)" represents 0.52525252..., and "0.5(25)"
# represents 0.52525252525..... , the strings represent the same number.
#
# Example 2:
#
# Input: s = "0.1666(6)", t = "0.166(66)"
# Output: true
#
# Example 3:
#
# Input: s = "0.9(9)", t = "1."
# Output: true
# Explanation: "0.9(9)" represents 0.999999999... repeated forever, which
# equals 1. [See this link for an explanation.]
# "1." represents the number 1, which is formed correctly: (IntegerPart) = "1"
# and (NonRepeatingPart) = "".
#
# Constraints:
#
# Each part consists only of digits.
#
# The <IntegerPart> does not have leading zeros (except for the zero itself).
#
# 1 <= <IntegerPart>.length <= 4
#
# 0 <= <NonRepeatingPart>.length <= 4
#
# 1 <= <RepeatingPart>.length <= 4
#

# @lc code=start
from fractions import Fraction


class Solution:
    def isRationalEqual(self, s: str, t: str) -> bool:
        """
        Interview explanation:
        Parse decimal strings that may include repeating parentheses into exact
        Fraction values and compare. Non-repeating + repeating = a + b/(10^k)
        + r / (10^k * (10^m - 1)).

        Algorithm:
        - parse(str) → Fraction:
          - Split integer, non-rep, rep parts from i.d(e) form
          - value = int + nonrep/10^len(nonrep) + rep / (10^len(nonrep)*(10^len(rep)-1))
        - Return parse(s) == parse(t)

        Complexity: O(L) time/space for string length L.
        """
        def parse(num: str) -> Fraction:
            if '.' not in num:
                return Fraction(int(num), 1)
            integer, rest = num.split('.')
            nonrep = ''
            rep = ''
            if '(' in rest:
                nonrep, rep = rest.split('(')
                rep = rep.rstrip(')')
            else:
                nonrep = rest
            val = Fraction(int(integer or '0'), 1)
            if nonrep:
                val += Fraction(int(nonrep), 10 ** len(nonrep))
            if rep:
                # repeating starts after nonrep digits
                denom = (10 ** len(rep) - 1) * (10 ** len(nonrep))
                val += Fraction(int(rep), denom)
            return val

        return parse(s) == parse(t)
# @lc code=end

