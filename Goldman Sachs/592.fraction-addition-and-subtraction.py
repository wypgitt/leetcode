#
# @lc app=leetcode id=592 lang=python3
#
# [592] Fraction Addition and Subtraction
#
# https://leetcode.com/problems/fraction-addition-and-subtraction/description/
#
# algorithms
# Medium (66.43%)
# Likes:    891
# Dislikes: 696
# Total Accepted:    138.2K
# Total Submissions: 208K
# Testcase Example:  '"-1/2+1/2"'
#
# Given a string expression representing an expression of fraction addition and
# subtraction, return the calculation result in string format.
# 
# The final result should be an irreducible fraction. If your final result is
# an integer, change it to the format of a fraction that has a denominator 1.
# So in this case, 2 should be converted to 2/1.
# 
# 
# Example 1:
# 
# 
# Input: expression = "-1/2+1/2"
# Output: "0/1"
# 
# 
# Example 2:
# 
# 
# Input: expression = "-1/2+1/2+1/3"
# Output: "1/3"
# 
# 
# Example 3:
# 
# 
# Input: expression = "1/3-1/2"
# Output: "-1/6"
# 
# 
# 
# Constraints:
# 
# 
# The input string only contains '0' to '9', '/', '+' and '-'. So does the
# output.
# Each fraction (input and output) has the format ±numerator/denominator. If
# the first input fraction or the output is positive, then '+' will be
# omitted.
# The input only contains valid irreducible fractions, where the numerator and
# denominator of each fraction will always be in the range [1, 10]. If the
# denominator is 1, it means this fraction is actually an integer in a fraction
# format defined above.
# The number of given fractions will be in the range [1, 10].
# The numerator and denominator of the final result are guaranteed to be valid
# and in the range of 32-bit int.
# 
# 
#

# @lc code=start
import math
import re


class Solution:
    def fractionAddition(self, expression: str) -> str:
        numerator = 0
        denominator = 1
        for a, b in re.findall(r'([+-]?\d+)/(\d+)', expression):
            n, d = int(a), int(b)
            numerator = numerator * d + n * denominator
            denominator *= d
            g = math.gcd(abs(numerator), denominator)
            numerator //= g
            denominator //= g
        return f"{numerator}/{denominator}"
# @lc code=end

"""
Interview explanation:
Parse each signed fraction and maintain a running reduced fraction. To add n/d to a/b, compute (a*d + n*b)/(b*d), then divide by the gcd to keep numbers small.

Data structure: regular expression tokenization avoids manual sign parsing; two integers store the current fraction.

Edge cases: the first term may be unsigned or signed. A zero numerator reduces to 0/1 because gcd(abs(0), denominator) is denominator.

Complexity: O(t log V) for t fractions, where gcd cost depends on integer size V. Space is O(1) apart from regex matches.
"""
