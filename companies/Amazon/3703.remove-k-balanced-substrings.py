#
# @lc app=leetcode id=3703 lang=python3
#
# [3703] Remove K-Balanced Substrings
#
# https://leetcode.com/problems/remove-k-balanced-substrings/description/
#
# algorithms
# Medium (33.02%)
# Likes:    134
# Dislikes: 11
# Total Accepted:    20.6K
# Total Submissions: 62.5K
# Testcase Example:  "\"(())\"\n1"
#
#
# You are given a string s consisting of '(' and ')', and an integer k.
#
# A string is k-balanced if it is exactly k consecutive '(' followed by k
# consecutive ')', i.e., '(' * k + ')' * k.
#
# For example, if k = 3, k-balanced is "((()))".
#
# You must repeatedly remove all non-overlapping k-balanced substrings
# from s, and then join the remaining parts. Continue this process until
# no k-balanced substring exists.
#
# Return the final string after all possible removals.
#
# ​​​​​​​Example 1:
#
# Input: s = "(())", k = 1
#
# Output: ""
#
# Explanation:
#
# k-balanced substring is "()"
#
#                         Step
#                         Current s
#                         k-balanced
#                         Result s
#
#                         1
#                         (())
#                         (())
#                         ()
#
#                         2
#                         ()
#                         ()
#                         Empty
#
# Thus, the final string is "".
#
# Example 2:
#
# Input: s = "(()(", k = 1
#
# Output: "(("
#
# Explanation:
#
# k-balanced substring is "()"
#
#                         Step
#                         Current s
#                         k-balanced
#                         Result s
#
#                         1
#                         (()(
#                         (()(
#                         ((
#
#                         2
#                         ((
#                         -
#                         ((
#
# Thus, the final string is "((".
#
# Example 3:
#
# Input: s = "((()))()()()", k = 3
#
# Output: "()()()"
#
# Explanation:
#
# k-balanced substring is "((()))"
#
#                         Step
#                         Current s
#                         k-balanced
#                         Result s
#
#                         1
#                         ((()))()()()
#                         ((()))()()()
#                         ()()()
#
#                         2
#                         ()()()
#                         -
#                         ()()()
#
# Thus, the final string is "()()()".
#
# Constraints:
#
# 2 <= s.length <= 10^5
#
# s consists only of '(' and ')'.
#
# 1 <= k <= s.length / 2
#

# @lc code=start

class Solution:
    def removeSubstring(self, s: str, k: int) -> str:
        """
        Interview explanation:
        Repeatedly delete blocks '('*k + ')'*k. A run-length stack lets us
        collapse matches in one left-to-right pass.

        Algorithm:
        - Maintain stack of [char, consecutive count].
        - After each push, while top is ')'*>=k above '('*>=k, subtract k from both
          and drop zero-count runs.

        Complexity: O(n) time, O(n) space.
        """
        stack: list[list] = []
        for ch in s:
            if stack and stack[-1][0] == ch:
                stack[-1][1] += 1
            else:
                stack.append([ch, 1])
            while (
                len(stack) >= 2
                and stack[-1][0] == ")"
                and stack[-1][1] >= k
                and stack[-2][0] == "("
                and stack[-2][1] >= k
            ):
                stack[-1][1] -= k
                stack[-2][1] -= k
                if stack[-1][1] == 0:
                    stack.pop()
                if stack[-1][1] == 0:
                    stack.pop()
        return "".join(c * cnt for c, cnt in stack)
# @lc code=end
