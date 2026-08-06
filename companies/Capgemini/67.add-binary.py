#
# @lc app=leetcode id=67 lang=python3
#
# [67] Add Binary
#
# https://leetcode.com/problems/add-binary/description/
#
# algorithms
# Easy (58.43%)
# Likes:    10878
# Dislikes: 1121
# Total Accepted:    2.4M
# Total Submissions: 4.2M
# Testcase Example:  "\"11\""
#
# Given two binary strings a and b, return their sum as a binary string.
#
# Example 1:
#
# Input: a = "11", b = "1"
# Output: "100"
#
# Example 2:
#
# Input: a = "1010", b = "1011"
# Output: "10101"
#
# Constraints:
#
# 1 <= a.length, b.length <= 10^4
#
# a and b consist only of '0' or '1' characters.
#
# Each string does not contain leading zeros except for the zero itself.
#

# @lc code=start
class Solution:
    def addBinary(self, a: str, b: str) -> str:
        """
        Interview explanation:
        Same idea as adding two numbers digit-by-digit, but in base 2. Work from
        the least significant bit so carry propagates naturally.

        Algorithm:
        - i, j start at the ends of a and b; carry = 0.
        - While either pointer is valid or carry remains:
          - Sum the current bits (0 if exhausted) plus carry.
          - Append sum % 2; set carry = sum // 2.
        - Reverse the collected bits into the result string.

        Complexity: O(max(len(a), len(b))) time and space.
        """
        i, j = len(a) - 1, len(b) - 1
        carry = 0
        bits = []

        while i >= 0 or j >= 0 or carry:
            total = carry
            if i >= 0:
                total += int(a[i])
                i -= 1
            if j >= 0:
                total += int(b[j])
                j -= 1
            bits.append(str(total % 2))
            carry = total // 2

        return ''.join(reversed(bits))
# @lc code=end
