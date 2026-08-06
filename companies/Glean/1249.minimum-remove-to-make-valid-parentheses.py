#
# @lc app=leetcode id=1249 lang=python3
#
# [1249] Minimum Remove to Make Valid Parentheses
#
# https://leetcode.com/problems/minimum-remove-to-make-valid-parentheses/description/
#
# algorithms
# Medium (71.55%)
# Likes:    7433
# Dislikes: 168
# Total Accepted:    1.1M
# Total Submissions: 1.5M
# Testcase Example:  "\"lee(t(c)o)de)\""
#
# Given a string s of '(' , ')' and lowercase English characters.
#
# Your task is to remove the minimum number of parentheses ( '(' or ')', in any
# positions ) so that the resulting parentheses string is valid and return any
# valid string.
#
# Formally, a parentheses string is valid if and only if:
#
# It is the empty string, contains only lowercase characters, or
#
# It can be written as AB (A concatenated with B), where A and B are valid
# strings, or
#
# It can be written as (A), where A is a valid string.
#
# Example 1:
#
# Input: s = "lee(t(c)o)de)"
# Output: "lee(t(c)o)de"
# Explanation: "lee(t(co)de)" , "lee(t(c)ode)" would also be accepted.
#
# Example 2:
#
# Input: s = "a)b(c)d"
# Output: "ab(c)d"
#
# Example 3:
#
# Input: s = "))(("
# Output: ""
# Explanation: An empty string is also valid.
#
# Constraints:
#
# 1 <= s.length <= 10^5
#
# s[i] is either '(' , ')', or lowercase English letter.
#


# @lc code=start
class Solution:
    def minRemoveToMakeValid(self, s: str) -> str:
        """
        Interview explanation:
        Remove minimum parentheses to make valid. Stack indices of '('; mark
        unmatched ')' and leftover '(' for deletion; rebuild string.

        Algorithm:
        - First pass: stack of '(' indices; mark bad ')' ; leftover '(' also bad
        - Second pass: skip marked indices

        Complexity: O(n) time/space.
        """
        s = list(s)
        stack = []
        for i, ch in enumerate(s):
            if ch == '(':
                stack.append(i)
            elif ch == ')':
                if stack:
                    stack.pop()
                else:
                    s[i] = ''
        for i in stack:
            s[i] = ''
        return ''.join(s)

    def minRemoveToMakeValid_twopass(self, s: str) -> str:
        """
        Interview explanation:
        Alternate: left-to-right remove extra ')'; reverse and remove extra '('
        (treat as ')' in reverse scan).

        Algorithm:
        - Helper build keeping balance>=0; apply twice with reverse for '('

        Complexity: O(n) time, O(n) space.
        """
        def clean(t: str, op: str, cl: str) -> str:
            bal = 0
            out = []
            for ch in t:
                if ch == op:
                    bal += 1
                    out.append(ch)
                elif ch == cl:
                    if bal == 0:
                        continue
                    bal -= 1
                    out.append(ch)
                else:
                    out.append(ch)
            return ''.join(out)

        t = clean(s, '(', ')')
        t = clean(t[::-1], ')', '(')
        return t[::-1]
# @lc code=end
