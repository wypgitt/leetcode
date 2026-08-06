#
# @lc app=leetcode id=1614 lang=python3
#
# [1614] Maximum Nesting Depth of the Parentheses
#
# https://leetcode.com/problems/maximum-nesting-depth-of-the-parentheses/description/
#
# algorithms
# Easy (85.03%)
# Likes:    2877
# Dislikes: 526
# Total Accepted:    591K
# Total Submissions: 695K
# Testcase Example:  "\"(1+(2*3)+((8)/4))+1\""
#
# Given a valid parentheses string s, return the nesting depth of s. The
# nesting depth is the maximum number of nested parentheses.
#
# Example 1:
#
# Input: s = "(1+(2*3)+((8)/4))+1"
#
# Output: 3
#
# Explanation:
#
# Digit 8 is inside of 3 nested parentheses in the string.
#
# Example 2:
#
# Input: s = "(1)+((2))+(((3)))"
#
# Output: 3
#
# Explanation:
#
# Digit 3 is inside of 3 nested parentheses in the string.
#
# Example 3:
#
# Input: s = "()(())((()()))"
#
# Output: 3
#
# Constraints:
#
# 1 <= s.length <= 100
#
# s consists of digits 0-9 and characters '+', '-', '*', '/', '(', and ')'.
#
# It is guaranteed that parentheses expression s is a VPS.
#

# @lc code=start
class Solution:
    def maxDepth(self, s: str) -> int:
        """
        Interview explanation:
        Nesting depth of VPS is max balance of parentheses (ignore other chars).

        Algorithm (counter):
        - cur +=1 on '('; -=1 on ')'; track max cur.

        Complexity: O(n) time, O(1) space.
        """
        cur = ans = 0
        for ch in s:
            if ch == "(":
                cur += 1
                ans = max(ans, cur)
            elif ch == ")":
                cur -= 1
        return ans

    def maxDepth_stack(self, s: str) -> int:
        """
        Interview explanation:
        Alternate stack view: push '('; pop on ')'; max stack size is depth.

        Algorithm (stack):
        - Maintain stack of '(' only; ans = max len(stack).

        Complexity: O(n) time/space.
        """
        st = []
        ans = 0
        for ch in s:
            if ch == "(":
                st.append(ch)
                ans = max(ans, len(st))
            elif ch == ")":
                st.pop()
        return ans
# @lc code=end
