#
# @lc app=leetcode id=709 lang=python3
#
# [709] To Lower Case
#
# https://leetcode.com/problems/to-lower-case/description/
#
# algorithms
# Easy (85.06%)
# Likes:    2067
# Dislikes: 2803
# Total Accepted:    775K
# Total Submissions: 911K
# Testcase Example:  "\"Hello\""
#
# Given a string s, return the string after replacing every uppercase letter
# with the same lowercase letter.
#
# Example 1:
#
# Input: s = "Hello"
# Output: "hello"
#
# Example 2:
#
# Input: s = "here"
# Output: "here"
#
# Example 3:
#
# Input: s = "LOVELY"
# Output: "lovely"
#
# Constraints:
#
# 1 <= s.length <= 100
#
# s consists of printable ASCII characters.
#

# @lc code=start
class Solution:
    def toLowerCase(self, s: str) -> str:
        """
        Interview explanation:
        Convert uppercase ASCII letters to lowercase without library shortcuts
        if desired: 'A'..'Z' map by +32. Using str.lower() is also acceptable.

        Algorithm:
        - Build new string: if 'A'<=c<='Z' then chr(ord(c)+32) else c.

        Complexity: O(n) time, O(n) space.
        """
        out = []
        for c in s:
            if "A" <= c <= "Z":
                out.append(chr(ord(c) + 32))
            else:
                out.append(c)
        return "".join(out)
# @lc code=end
