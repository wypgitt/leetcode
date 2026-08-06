#
# @lc app=leetcode id=1190 lang=python3
#
# [1190] Reverse Substrings Between Each Pair of Parentheses
#
# https://leetcode.com/problems/reverse-substrings-between-each-pair-of-parentheses/description/
#
# algorithms
# Medium (72.07%)
# Likes:    2960
# Dislikes: 132
# Total Accepted:    249K
# Total Submissions: 346K
# Testcase Example:  "\"(abcd)\""
#
# You are given a string s that consists of lower case English letters and
# brackets.
#
# Reverse the strings in each pair of matching parentheses, starting from the
# innermost one.
#
# Your result should not contain any brackets.
#
# Example 1:
#
# Input: s = "(abcd)"
# Output: "dcba"
#
# Example 2:
#
# Input: s = "(u(love)i)"
# Output: "iloveu"
# Explanation: The substring "love" is reversed first, then the whole string is
# reversed.
#
# Example 3:
#
# Input: s = "(ed(et(oc))el)"
# Output: "leetcode"
# Explanation: First, we reverse the substring "oc", then "etco", and finally,
# the whole string.
#
# Constraints:
#
# 1 <= s.length <= 2000
#
# s only contains lower case English characters and parentheses.
#
# It is guaranteed that all parentheses are balanced.
#

# @lc code=start

class Solution:
    def reverseParentheses(self, s: str) -> str:
        """
        Interview explanation:
        Stack of strings/chars: on '(', push marker; on ')', pop until marker
        and reverse that segment back onto the stack; letters append. Drop
        brackets in the final join.

        Algorithm (stack):
        - stack of chars. '(': push. letter: push. ')': pop until '(', reverse
          popped chars and push them back.
        - Join stack.

        Complexity: O(n^2) worst case (naive reverse), O(n) space.
        """
        stack = []
        for ch in s:
            if ch == ')':
                segment = []
                while stack and stack[-1] != '(':
                    segment.append(stack.pop())
                if stack:
                    stack.pop()  # '('
                stack.extend(segment)  # already reversed by pop order
            else:
                stack.append(ch)
        return ''.join(stack)

    def reverseParentheses_wormhole(self, s: str) -> str:
        """
        Interview explanation:
        Alternate O(n): pair matching parentheses ("wormholes"). Traverse with
        direction; on '(' or ')' jump to pair and flip direction; collect letters.

        Algorithm:
        - Build pair[i] via stack of indices.
        - i=0, d=1; while in range: if bracket, i=pair[i], d=-d; else append.
          i += d.

        Complexity: O(n) time, O(n) space.
        """
        n = len(s)
        pair = [0] * n
        st = []
        for i, ch in enumerate(s):
            if ch == '(':
                st.append(i)
            elif ch == ')':
                j = st.pop()
                pair[i] = j
                pair[j] = i

        ans = []
        i, d = 0, 1
        while i < n:
            if s[i] in '()':
                i = pair[i]
                d = -d
            else:
                ans.append(s[i])
            i += d
        return ''.join(ans)
# @lc code=end
