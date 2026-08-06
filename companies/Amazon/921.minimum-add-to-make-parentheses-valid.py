#
# @lc app=leetcode id=921 lang=python3
#
# [921] Minimum Add to Make Parentheses Valid
#
# https://leetcode.com/problems/minimum-add-to-make-parentheses-valid/description/
#
# algorithms
# Medium (74.29%)
# Likes:    5001
# Dislikes: 251
# Total Accepted:    728K
# Total Submissions: 980K
# Testcase Example:  "\"())\""
#
# A parentheses string is valid if and only if:
#
# It is the empty string,
#
# It can be written as AB (A concatenated with B), where A and B are valid
# strings, or
#
# It can be written as (A), where A is a valid string.
#
# You are given a parentheses string s. In one move, you can insert a
# parenthesis at any position of the string.
#
# For example, if s = "()))", you can insert an opening parenthesis to be
# "(()))" or a closing parenthesis to be "())))".
#
# Return the minimum number of moves required to make s valid.
#
# Example 1:
#
# Input: s = "())"
# Output: 1
#
# Example 2:
#
# Input: s = "((("
# Output: 3
#
# Constraints:
#
# 1 <= s.length <= 1000
#
# s[i] is either '(' or ')'.
#

# @lc code=start
class Solution:
    def minAddToMakeValid(self, s: str) -> int:
        """
        Interview explanation:
        Track balance of unmatched '('. Each ')' with balance 0 needs a prior
        '('. Remaining unmatched '(' at the end also need closing inserts.

        Algorithm (balance counter):
        - bal = adds = 0
        - For '(': bal += 1
        - For ')': if bal: bal -= 1 else adds += 1
        - Return adds + bal

        Complexity: O(n) time, O(1) space.
        """
        bal = adds = 0
        for c in s:
            if c == '(':
                bal += 1
            elif bal:
                bal -= 1
            else:
                adds += 1
        return adds + bal

    def minAddToMakeValid_stack(self, s: str) -> int:
        """
        Interview explanation:
        Alternate classic: simulate with a stack of unmatched '('. Unmatched
        ')' and leftover stack size sum to the answer.

        Algorithm:
        - stack=[]; adds=0
        - '(': push; ')': pop if stack else adds++
        - Return adds + len(stack)

        Complexity: O(n) time, O(n) space.
        """
        stack = []
        adds = 0
        for c in s:
            if c == '(':
                stack.append(c)
            elif stack:
                stack.pop()
            else:
                adds += 1
        return adds + len(stack)
# @lc code=end

