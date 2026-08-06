#
# @lc app=leetcode id=415 lang=python3
#
# [415] Add Strings
#
# https://leetcode.com/problems/add-strings/description/
#
# algorithms
# Easy (52.21%)
# Likes:    5506
# Dislikes: 836
# Total Accepted:    974K
# Total Submissions: 1.9M
# Testcase Example:  "\"11\""
#
# Given two non-negative integers, num1 and num2 represented as string, return
# the sum of num1 and num2 as a string.
#
# You must solve the problem without using any built-in library for handling
# large integers (such as BigInteger). You must also not convert the inputs to
# integers directly.
#
# Example 1:
#
# Input: num1 = "11", num2 = "123"
# Output: "134"
#
# Example 2:
#
# Input: num1 = "456", num2 = "77"
# Output: "533"
#
# Example 3:
#
# Input: num1 = "0", num2 = "0"
# Output: "0"
#
# Constraints:
#
# 1 <= num1.length, num2.length <= 10^4
#
# num1 and num2 consist of only digits.
#
# num1 and num2 don't have any leading zeros except for the zero itself.
#

# @lc code=start

class Solution:
    def addStrings(self, num1: str, num2: str) -> str:
        """
        Interview explanation:
        Schoolbook addition from the least significant digit with a carry,
        without converting the whole strings to integers.

        Algorithm:
        - i,j from ends; while digits or carry: sum digits+carry; append digit.
        - Reverse result string.

        Complexity: O(max(m,n)) time, O(max(m,n)) space.
        """
        i, j = len(num1) - 1, len(num2) - 1
        carry = 0
        out = []
        while i >= 0 or j >= 0 or carry:
            a = ord(num1[i]) - 48 if i >= 0 else 0
            b = ord(num2[j]) - 48 if j >= 0 else 0
            s = a + b + carry
            out.append(str(s % 10))
            carry = s // 10
            i -= 1
            j -= 1
        return "".join(reversed(out))
# @lc code=end
