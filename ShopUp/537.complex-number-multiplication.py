#
# @lc app=leetcode id=537 lang=python3
#
# [537] Complex Number Multiplication
#
# https://leetcode.com/problems/complex-number-multiplication/description/
#
# algorithms
# Medium (73.50%)
# Likes:    757
# Dislikes: 1257
# Total Accepted:    115.5K
# Total Submissions: 157.1K
# Testcase Example:  '"1+1i"\n"1+1i"'
#
# A complex number can be represented as a string on the form "real+imaginaryi"
# where:
# 
# 
# real is the real part and is an integer in the range [-100, 100].
# imaginary is the imaginary part and is an integer in the range [-100,
# 100].
# i^2 == -1.
# 
# 
# Given two complex numbers num1 and num2 as strings, return a string of the
# complex number that represents their multiplications.
# 
# 
# Example 1:
# 
# 
# Input: num1 = "1+1i", num2 = "1+1i"
# Output: "0+2i"
# Explanation: (1 + i) * (1 + i) = 1 + i2 + 2 * i = 2i, and you need convert it
# to the form of 0+2i.
# 
# 
# Example 2:
# 
# 
# Input: num1 = "1+-1i", num2 = "1+-1i"
# Output: "0+-2i"
# Explanation: (1 - i) * (1 - i) = 1 + i2 - 2 * i = -2i, and you need convert
# it to the form of 0+-2i.
# 
# 
# 
# Constraints:
# 
# 
# num1 and num2 are valid complex numbers.
# 
# 
#

# @lc code=start
class Solution:
    def complexNumberMultiply(self, num1: str, num2: str) -> str:
        def parse(num: str) -> tuple[int, int]:
            real, imag = num[:-1].split('+')
            return int(real), int(imag)

        a, b = parse(num1)
        c, d = parse(num2)
        return f"{a * c - b * d}+{a * d + b * c}i"
# @lc code=end

"""
Interview explanation:
Parse each number as a + bi, then multiply using (a + bi)(c + di) = (ac - bd) + (ad + bc)i.

Data structure: no special structure is required; a helper parser returns integer pairs.

Edge cases: negative real or imaginary parts are handled by int(), and the format always contains '+' and trailing 'i' per constraints.

Complexity: O(1) time and space because input lengths are bounded; more generally O(len(num1)+len(num2)) parsing time.
"""
