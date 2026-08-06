#
# @lc app=leetcode id=844 lang=python3
#
# [844] Backspace String Compare
#
# https://leetcode.com/problems/backspace-string-compare/description/
#
# algorithms
# Easy (50.14%)
# Likes:    8020
# Dislikes: 386
# Total Accepted:    1.1M
# Total Submissions: 2.2M
# Testcase Example:  "\"ab#c\""
#
# Given two strings s and t, return true if they are equal when both are typed
# into empty text editors. '#' means a backspace character.
#
# Note that after backspacing an empty text, the text will continue empty.
#
# Example 1:
#
# Input: s = "ab#c", t = "ad#c"
# Output: true
# Explanation: Both s and t become "ac".
#
# Example 2:
#
# Input: s = "ab##", t = "c#d#"
# Output: true
# Explanation: Both s and t become "".
#
# Example 3:
#
# Input: s = "a#c", t = "b"
# Output: false
# Explanation: s becomes "c" while t becomes "b".
#
# Constraints:
#
# 1 <= s.length, t.length <= 200
#
# s and t only contain lowercase letters and '#' characters.
#
# Follow up: Can you solve it in O(n) time and O(1) space?
#

# @lc code=start

class Solution:
    def backspaceCompare(self, s: str, t: str) -> bool:
        """
        Interview explanation:
        Simulate typing with a stack: push letters, pop on '#'. Compare final
        stacks / strings.

        Algorithm (stack):
        - build(s): for c in s: if c!='#': push else pop if stack.
        - Return build(s)==build(t).

        Complexity: O(n+m) time, O(n+m) space.
        """
        def build(x: str) -> list:
            st = []
            for c in x:
                if c != "#":
                    st.append(c)
                elif st:
                    st.pop()
            return st

        return build(s) == build(t)

    def backspaceCompare_two_pointers(self, s: str, t: str) -> bool:
        """
        Interview explanation:
        O(1)-space alternate: scan from the right with skip counters for '#'.

        Algorithm:
        - Two pointers from ends; skip backspaced chars; compare next valid chars.

        Complexity: O(n+m) time, O(1) space.
        """
        def next_valid(string: str, i: int):
            skip = 0
            while i >= 0:
                if string[i] == "#":
                    skip += 1
                    i -= 1
                elif skip:
                    skip -= 1
                    i -= 1
                else:
                    break
            return i

        i, j = len(s) - 1, len(t) - 1
        while True:
            i = next_valid(s, i)
            j = next_valid(t, j)
            if i < 0 and j < 0:
                return True
            if i < 0 or j < 0 or s[i] != t[j]:
                return False
            i -= 1
            j -= 1
# @lc code=end
