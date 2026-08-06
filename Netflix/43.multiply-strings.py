#
# @lc app=leetcode id=43 lang=python3
#
# [43] Multiply Strings
#
# https://leetcode.com/problems/multiply-strings/description/
#
# algorithms
# Medium (44.10%)
# Likes:    7763
# Dislikes: 3690
# Total Accepted:    1.2M
# Total Submissions: 2.6M
# Testcase Example:  '"2"\n"3"'
#
# Given two non-negative integers num1 and num2 represented as strings, return
# the product of num1 and num2, also represented as a string.
# 
# Note: You must not use any built-in BigInteger library or convert the inputs
# to integer directly.
# 
# 
# Example 1:
# Input: num1 = "2", num2 = "3"
# Output: "6"
# Example 2:
# Input: num1 = "123", num2 = "456"
# Output: "56088"
# 
# 
# Constraints:
# 
# 
# 1 <= num1.length, num2.length <= 200
# num1 and num2 consist of digits only.
# Both num1 and num2 do not contain any leading zero, except the number 0
# itself.
# 
# 
#

# @lc code=start
from typing import List, Optional
class Solution:
    def multiply(self, num1: str, num2: str) -> str:
        """
        Interview explanation:
        Simulate grade-school multiplication. Digit i from num1 and digit j from
        num2 contribute to result positions i+j and i+j+1 in a length m+n array.
        The array is the right structure because it lets us accumulate carries
        by position without converting the full strings to integers.

        Edge cases and tests:
        - Any operand "0" returns "0".
        - Carry propagation across several positions, e.g. 99 * 99.
        - Leading zeroes in the result array are stripped.

        Complexity: O(m*n) time, O(m+n) space.
        """
        if num1 == '0' or num2 == '0':
            return '0'

        m, n = len(num1), len(num2)
        res = [0] * (m + n)

        for i in range(m - 1, -1, -1):
            for j in range(n - 1, -1, -1):
                product = (ord(num1[i]) - ord('0')) * (ord(num2[j]) - ord('0'))
                total = product + res[i + j + 1]
                res[i + j + 1] = total % 10
                res[i + j] += total // 10

        start = 0
        while start < len(res) and res[start] == 0:
            start += 1
        return ''.join(map(str, res[start:]))
# @lc code=end


