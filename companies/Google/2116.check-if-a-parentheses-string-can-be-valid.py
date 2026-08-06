#
# @lc app=leetcode id=2116 lang=python3
#
# [2116] Check if a Parentheses String Can Be Valid
#
# https://leetcode.com/problems/check-if-a-parentheses-string-can-be-valid/description/
#
# algorithms
# Medium (45.23%)
# Likes:    2049
# Dislikes: 135
# Total Accepted:    158.7K
# Total Submissions: 350.8K
# Testcase Example:  "\"))()))\"\n\"010100\""
#
# A parentheses string is a non-empty string consisting only of '(' and ')'. It
# is valid if any of the following conditions is true:
#
#
# It is ().
#
#
# It can be written as AB (A concatenated with B), where A and B are valid
# parentheses strings.
#
#
# It can be written as (A), where A is a valid parentheses string.
#
# You are given a parentheses string s and a string locked, both of length n.
# locked is a binary string consisting only of '0's and '1's. For each index i
# of locked,
#
#
# If locked[i] is '1', you cannot change s[i].
#
#
# But if locked[i] is '0', you can change s[i] to either '(' or ')'.
#
# Return true if you can make s a valid parentheses string. Otherwise, return
# false.
#
#
#
# Example 1:
#
# Input: s = "))()))", locked = "010100"
# Output: true
# Explanation: locked[1] == '1' and locked[3] == '1', so we cannot change s[1]
# or s[3].
# We change s[0] and s[4] to '(' while leaving s[2] and s[5] unchanged to make s
# valid.
#
# Example 2:
#
# Input: s = "()()", locked = "0000"
# Output: true
# Explanation: We do not need to make any changes because s is already valid.
#
# Example 3:
#
# Input: s = ")", locked = "0"
# Output: false
# Explanation: locked permits us to change s[0].
# Changing s[0] to either '(' or ')' will not make s valid.
#
# Example 4:
#
# Input: s = "(((())(((())", locked = "111111010111"
# Output: true
# Explanation: locked permits us to change s[6] and s[8].
# We change s[6] and s[8] to ')' to make s valid.
#
#
#
# Constraints:
#
#
# n == s.length == locked.length
#
#
# 1 <= n <= 10^5
#
#
# s[i] is either '(' or ')'.
#
#
# locked[i] is either '0' or '1'.
#


# @lc code=start
class Solution:
    def canBeValid(self, s: str, locked: str) -> bool:
        """
        Interview explanation:
        locked[i]=='0' means s[i] can flip to '(' or ')'. Check if s can become
        a valid parentheses string.

        Algorithm:
        - Length must be even.
        - Left-to-right: treat unlocked as wild; balance upper bound; fail if
          too many locked ')'.
        - Right-to-left: symmetric for locked '('.

        Complexity: O(n) time, O(1) space.
        """
        n = len(s)
        if n % 2:
            return False
        bal = 0
        for i in range(n):
            if locked[i] == '0' or s[i] == '(':
                bal += 1
            else:
                bal -= 1
            if bal < 0:
                return False
        bal = 0
        for i in range(n - 1, -1, -1):
            if locked[i] == '0' or s[i] == ')':
                bal += 1
            else:
                bal -= 1
            if bal < 0:
                return False
        return True
# @lc code=end

