#
# @lc app=leetcode id=856 lang=python3
#
# [856] Score of Parentheses
#
# https://leetcode.com/problems/score-of-parentheses/description/
#
# algorithms
# Medium (63.49%)
# Likes:    5634
# Dislikes: 240
# Total Accepted:    229K
# Total Submissions: 361K
# Testcase Example:  "\"()\""
#
# Given a balanced parentheses string s, return the score of the string.
#
# The score of a balanced parentheses string is based on the following rule:
#
# "()" has score 1.
#
# AB has score A + B, where A and B are balanced parentheses strings.
#
# (A) has score 2 * A, where A is a balanced parentheses string.
#
# Example 1:
#
# Input: s = "()"
# Output: 1
#
# Example 2:
#
# Input: s = "(())"
# Output: 2
#
# Example 3:
#
# Input: s = "()()"
# Output: 2
#
# Constraints:
#
# 2 <= s.length <= 50
#
# s consists of only '(' and ')'.
#
# s is a balanced parentheses string.
#

# @lc code=start

class Solution:
    def scoreOfParentheses(self, s: str) -> int:
        """
        Interview explanation:
        Stack of scores: on '(': push 0; on ')': pop v, add max(2*v, 1) to
        new top. Classic stack scoring.

        Algorithm:
        - stack=[0]; for c: if (: push 0 else: v=pop; stack[-1]+=max(2*v,1).

        Complexity: O(n) time, O(n) space.
        """
        stack = [0]
        for c in s:
            if c == "(":
                stack.append(0)
            else:
                v = stack.pop()
                stack[-1] += max(2 * v, 1)
        return stack[0]

    def scoreOfParentheses_count(self, s: str) -> int:
        """
        Interview explanation:
        Depth/count alternate: score is sum of 2^depth for each "()" core.
        Track balance depth; when seeing "()", add 1<<depth.

        Algorithm:
        - bal=0; for i,c: if (: bal++ else: bal--; if s[i-1]=='(': ans += 1<<bal.

        Complexity: O(n) time, O(1) space.
        """
        ans = bal = 0
        for i, c in enumerate(s):
            if c == "(":
                bal += 1
            else:
                bal -= 1
                if s[i - 1] == "(":
                    ans += 1 << bal
        return ans
# @lc code=end
