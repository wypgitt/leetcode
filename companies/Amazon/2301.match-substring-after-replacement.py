#
# @lc app=leetcode id=2301 lang=python3
#
# [2301] Match Substring After Replacement
#
# https://leetcode.com/problems/match-substring-after-replacement/description/
#
# algorithms
# Hard (43.55%)
# Likes:    396
# Dislikes: 81
# Total Accepted:    18.6K
# Total Submissions: 42.6K
# Testcase Example:  "\"fool3e7bar\"\n\"leet\"\n[[\"e\",\"3\"],[\"t\",\"7\"],[\"t\",\"8\"]]"
#
# You are given two strings s and sub. You are also given a 2D character array
# mappings where mappings[i] = [old_i, new_i] indicates that you may perform the
# following operation any number of times:
#
#
# Replace a character old_i of sub with new_i.
#
# Each character in sub cannot be replaced more than once.
#
# Return true if it is possible to make sub a substring of s by replacing zero
# or more characters according to mappings. Otherwise, return false.
#
# A substring is a contiguous non-empty sequence of characters within a string.
#
#
#
# Example 1:
#
# Input: s = "fool3e7bar", sub = "leet", mappings =
# [["e","3"],["t","7"],["t","8"]]
# Output: true
# Explanation: Replace the first 'e' in sub with '3' and 't' in sub with '7'.
# Now sub = "l3e7" is a substring of s, so we return true.
#
# Example 2:
#
# Input: s = "fooleetbar", sub = "f00l", mappings = [["o","0"]]
# Output: false
# Explanation: The string "f00l" is not a substring of s and no replacements can
# be made.
# Note that we cannot replace '0' with 'o'.
#
# Example 3:
#
# Input: s = "Fool33tbaR", sub = "leetd", mappings =
# [["e","3"],["t","7"],["t","8"],["d","b"],["p","b"]]
# Output: true
# Explanation: Replace the first and second 'e' in sub with '3' and 'd' in sub
# with 'b'.
# Now sub = "l33tb" is a substring of s, so we return true.
#
#
#
# Constraints:
#
#
# 1 <= sub.length <= s.length <= 5000
#
#
# 0 <= mappings.length <= 1000
#
#
# mappings[i].length == 2
#
#
# old_i != new_i
#
#
# s and sub consist of uppercase and lowercase English letters and digits.
#
#
# old_i and new_i are either uppercase or lowercase English letters or digits.
#

# @lc code=start
from typing import List


class Solution:
    def matchReplacement(self, s: str, sub: str, mappings: List[List[str]]) -> bool:
        """
        Interview explanation:
        Check whether `sub` can match some substring of `s` after optionally
        replacing characters via the given (old -> new) mappings.

        Algorithm:
        - Build a set of allowed replacements for each character (char can map
          to itself).
        - Slide a window of len(sub) over s; accept if every position is equal
          or allowed by mappings.

        Complexity: O(|s| * |sub|) time, O(|mappings|) space.
        """
        allow = {}
        for a, b in mappings:
            allow.setdefault(a, set()).add(b)
        m = len(sub)
        for i in range(len(s) - m + 1):
            ok = True
            for j in range(m):
                x, y = sub[j], s[i + j]
                if x != y and y not in allow.get(x, ()):
                    ok = False
                    break
            if ok:
                return True
        return False
# @lc code=end
