#
# @lc app=leetcode id=1249 lang=python3
#
# [1249] Minimum Remove to Make Valid Parentheses
#
# https://leetcode.com/problems/minimum-remove-to-make-valid-parentheses/description/
#
# algorithms
# Medium (71.43%)
# Likes:    7408
# Dislikes: 167
# Total Accepted:    1.1M
# Total Submissions: 1.5M
# Testcase Example:  '"lee(t(c)o)de)"'
#
# Given a string s of '(' , ')' and lowercase English characters.
# 
# Your task is to remove the minimum number of parentheses ( '(' or ')', in any
# positions ) so that the resulting parentheses string is valid and return any
# valid string.
# 
# Formally, a parentheses string is valid if and only if:
# 
# 
# It is the empty string, contains only lowercase characters, or
# It can be written as AB (A concatenated with B), where A and B are valid
# strings, or
# It can be written as (A), where A is a valid string.
# 
# 
# 
# Example 1:
# 
# 
# Input: s = "lee(t(c)o)de)"
# Output: "lee(t(c)o)de"
# Explanation: "lee(t(co)de)" , "lee(t(c)ode)" would also be accepted.
# 
# 
# Example 2:
# 
# 
# Input: s = "a)b(c)d"
# Output: "ab(c)d"
# 
# 
# Example 3:
# 
# 
# Input: s = "))(("
# Output: ""
# Explanation: An empty string is also valid.
# 
# 
# 
# Constraints:
# 
# 
# 1 <= s.length <= 10^5
# s[i] is either '(' , ')', or lowercase English letter.
# 
# 
#

# @lc code=start
class Solution:
    def minRemoveToMakeValid(self, s: str) -> str:
        stack = []
        remove = set()

        for i, ch in enumerate(s):
            if ch == "(":
                stack.append(i)
            elif ch == ")":
                if stack:
                    stack.pop()
                else:
                    remove.add(i)

        remove.update(stack)
        return "".join(ch for i, ch in enumerate(s) if i not in remove)
# @lc code=end

# Explanation
# -----------
# Scan the string and push indices of unmatched '(' onto a stack. When seeing
# ')', match it with the latest '(' if possible; otherwise mark that ')' for
# removal. After the scan, any indices still on the stack are unmatched '(' and
# must also be removed.
#
# A stack is appropriate because parentheses match in last-opened,
# first-closed order.
#
# Edge cases: extra closing parentheses at the front; extra opening
# parentheses at the end; letters are ignored and preserved.
#
# Time complexity: O(n).
# Space complexity: O(n) for stack/removal indices and the output.
