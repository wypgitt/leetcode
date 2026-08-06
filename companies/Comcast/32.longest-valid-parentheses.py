#
# @lc app=leetcode id=32 lang=python3
#
# [32] Longest Valid Parentheses
#
# https://leetcode.com/problems/longest-valid-parentheses/description/
#
# algorithms
# Hard (39.41%)
# Likes:    13418
# Dislikes: 469
# Total Accepted:    1.2M
# Total Submissions: 2.9M
# Testcase Example:  "\"(()\""
#
# Given a string containing just the characters '(' and ')', return the length
# of the longest valid (well-formed) parentheses substring.
#
# Example 1:
#
# Input: s = "(()"
# Output: 2
# Explanation: The longest valid parentheses substring is "()".
#
# Example 2:
#
# Input: s = ")()())"
# Output: 4
# Explanation: The longest valid parentheses substring is "()()".
#
# Example 3:
#
# Input: s = ""
# Output: 0
#
# Constraints:
#
# 0 <= s.length <= 3 * 10^4
#
# s[i] is '(', or ')'.
#

# @lc code=start
class Solution:
    def longestValidParentheses(self, s: str) -> int:
        """
        Interview explanation:
        Stack stores indices of unmatched '('. A sentinel -1 marks the base of
        the current valid segment so lengths compute as i - stack[-1].

        Algorithm:
        - Push -1 as a sentinel.
        - On '(': push index.
        - On ')': pop; if stack empty, push i as new base; else update
          best with i - stack[-1].

        Complexity: O(n) time, O(n) space.
        """
        return self.longestValidParentheses_stack(s)

    def longestValidParentheses_stack(self, s: str) -> int:
        """
        Interview explanation:
        Same stack approach as the primary method; exposed as an explicit
        classic alternate for interview discussion.

        Algorithm:
        - Index stack with sentinel -1.
        - Track max length after each successful match.

        Complexity: O(n) time, O(n) space.
        """
        stack = [-1]
        best = 0
        for i, ch in enumerate(s):
            if ch == "(":
                stack.append(i)
            else:
                stack.pop()
                if not stack:
                    stack.append(i)
                else:
                    best = max(best, i - stack[-1])
        return best

    def longestValidParentheses_dp(self, s: str) -> int:
        """
        Interview explanation:
        dp[i] = length of longest valid parentheses ending at index i.
        When s[i] == ')', look for a matching '(' immediately before the
        valid segment ending at i-1 (or at i-1 if that char is '(').

        Algorithm:
        - If s[i-1] == '(', dp[i] = dp[i-2] + 2 (when i >= 1).
        - Else if the char before the run ending at i-1 is '(', extend by
          dp[i-1] + 2 + dp[before that '('].

        Complexity: O(n) time, O(n) space.
        """
        n = len(s)
        if n < 2:
            return 0

        dp = [0] * n
        best = 0
        for i in range(1, n):
            if s[i] != ")":
                continue
            if s[i - 1] == "(":
                dp[i] = (dp[i - 2] if i >= 2 else 0) + 2
            else:
                j = i - dp[i - 1] - 1
                if j >= 0 and s[j] == "(":
                    dp[i] = dp[i - 1] + 2 + (dp[j - 1] if j >= 1 else 0)
            best = max(best, dp[i])
        return best
# @lc code=end
