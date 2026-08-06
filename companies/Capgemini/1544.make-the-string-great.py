#
# @lc app=leetcode id=1544 lang=python3
#
# [1544] Make The String Great
#
# https://leetcode.com/problems/make-the-string-great/description/
#
# algorithms
# Easy (68.64%)
# Likes:    3257
# Dislikes: 190
# Total Accepted:    426K
# Total Submissions: 620K
# Testcase Example:  "\"leEeetcode\""
#
# Given a string s of lower and upper case English letters.
#
# A good string is a string which doesn't have two adjacent characters s[i] and
# s[i + 1] where:
#
# 0 <= i <= s.length - 2
#
# s[i] is a lower-case letter and s[i + 1] is the same letter but in upper-case
# or vice-versa.
#
# To make the string good, you can choose two adjacent characters that make the
# string bad and remove them. You can keep doing this until the string becomes
# good.
#
# Return the string after making it good. The answer is guaranteed to be unique
# under the given constraints.
#
# Notice that an empty string is also good.
#
# Example 1:
#
# Input: s = "leEeetcode"
# Output: "leetcode"
# Explanation: In the first step, either you choose i = 1 or i = 2, both will
# result "leEeetcode" to be reduced to "leetcode".
#
# Example 2:
#
# Input: s = "abBAcC"
# Output: ""
# Explanation: We have many possible scenarios, and all lead to the same
# answer. For example:
# "abBAcC" --> "aAcC" --> "cC" --> ""
# "abBAcC" --> "abBA" --> "aA" --> ""
#
# Example 3:
#
# Input: s = "s"
# Output: "s"
#
# Constraints:
#
# 1 <= s.length <= 100
#
# s contains only lower and upper case English letters.
#

# @lc code=start
class Solution:
    def makeGood(self, s: str) -> str:
        """
        Interview explanation:
        Remove adjacent letters that are the same letter in different cases
        (e.g. 'aA') until string is "good". Stack: pop when bad pair with top.

        Algorithm:
        - stack=[]; for ch: if stack and stack[-1]!=ch and stack[-1].lower()==ch.lower():
          pop; else append.

        Complexity: O(n) time, O(n) space.
        """
        stack = []
        for ch in s:
            if stack and stack[-1] != ch and stack[-1].lower() == ch.lower():
                stack.pop()
            else:
                stack.append(ch)
        return "".join(stack)

    def makeGood_scan(self, s: str) -> str:
        """
        Interview explanation:
        Alternate: repeatedly scan/rebuild removing bad adjacent pairs until
        stable (clearer but slower).

        Algorithm:
        - While True: build new string skipping bad pairs; break when unchanged.

        Complexity: O(n^2) time, O(n) space.
        """
        def bad(a: str, b: str) -> bool:
            return a != b and a.lower() == b.lower()

        while True:
            out = []
            i = 0
            changed = False
            while i < len(s):
                if i + 1 < len(s) and bad(s[i], s[i + 1]):
                    i += 2
                    changed = True
                else:
                    out.append(s[i])
                    i += 1
            s = "".join(out)
            if not changed:
                return s
# @lc code=end
