#
# @lc app=leetcode id=2434 lang=python3
#
# [2434] Using a Robot to Print the Lexicographically Smallest String
#
# https://leetcode.com/problems/using-a-robot-to-print-the-lexicographically-smallest-string/description/
#
# algorithms
# Medium (62.19%)
# Likes:    1166
# Dislikes: 309
# Total Accepted:    110.6K
# Total Submissions: 177.9K
# Testcase Example:  "\"zza\""
#
# You are given a string s and a robot that currently holds an empty string t.
# Apply one of the following operations until s and t are both empty:
#
#
# Remove the first character of a string s and give it to the robot. The robot
# will append this character to the string t.
#
#
# Remove the last character of a string t and give it to the robot. The robot
# will write this character on paper.
#
# Return the lexicographically smallest string that can be written on the paper.
#
#
#
# Example 1:
#
# Input: s = "zza"
# Output: "azz"
# Explanation: Let p denote the written string.
# Initially p="", s="zza", t="".
# Perform first operation three times p="", s="", t="zza".
# Perform second operation three times p="azz", s="", t="".
#
# Example 2:
#
# Input: s = "bac"
# Output: "abc"
# Explanation: Let p denote the written string.
# Perform first operation twice p="", s="c", t="ba".
# Perform second operation twice p="ab", s="c", t="".
# Perform first operation p="ab", s="", t="c".
# Perform second operation p="abc", s="", t="".
#
# Example 3:
#
# Input: s = "bdda"
# Output: "addb"
# Explanation: Let p denote the written string.
# Initially p="", s="bdda", t="".
# Perform first operation four times p="", s="", t="bdda".
# Perform second operation four times p="addb", s="", t="".
#
#
#
# Constraints:
#
#
# 1 <= s.length <= 10^5
#
#
# s consists of only English lowercase letters.
#

# @lc code=start
from collections import Counter


class Solution:
    def robotWithString(self, s: str) -> str:
        """
        Interview explanation:
        Move chars from s onto stack t; pop t to paper anytime. Minimize paper
        lexicographically.

        Algorithm:
        - Remaining frequency; push from s; while stack top <= smallest remaining
          character, pop to answer.

        Complexity: O(n) time, O(n) space.
        """
        cnt = Counter(s)
        stack = []
        ans = []
        mn = "a"
        for ch in s:
            stack.append(ch)
            cnt[ch] -= 1
            while mn <= "z" and cnt[mn] == 0:
                mn = chr(ord(mn) + 1)
            while stack and stack[-1] <= mn:
                ans.append(stack.pop())
        return "".join(ans)

    def robotWithString_stack(self, s: str) -> str:
        """
        Interview explanation:
        Alternate identical stack+counter formulation.

        Algorithm:
        - Same as primary.

        Complexity: O(n) time, O(n) space.
        """
        return self.robotWithString(s)
# @lc code=end
