#
# @lc app=leetcode id=2060 lang=python3
#
# [2060] Check if an Original String Exists Given Two Encoded Strings
#
# https://leetcode.com/problems/check-if-an-original-string-exists-given-two-encoded-strings/description/
#
# algorithms
# Hard (43.38%)
# Likes:    328
# Dislikes: 165
# Total Accepted:    20.3K
# Total Submissions: 46.7K
# Testcase Example:  "\"internationalization\"\n\"i18n\""
#
# An original string, consisting of lowercase English letters, can be encoded by
# the following steps:
#
#
# Arbitrarily split it into a sequence of some number of non-empty substrings.
#
#
# Arbitrarily choose some elements (possibly none) of the sequence, and replace
# each with its length (as a numeric string).
#
#
# Concatenate the sequence as the encoded string.
#
# For example, one way to encode an original string "abcdefghijklmnop" might be:
#
#
# Split it as a sequence: ["ab", "cdefghijklmn", "o", "p"].
#
#
# Choose the second and third elements to be replaced by their lengths,
# respectively. The sequence becomes ["ab", "12", "1", "p"].
#
#
# Concatenate the elements of the sequence to get the encoded string: "ab121p".
#
# Given two encoded strings s1 and s2, consisting of lowercase English letters
# and digits 1-9 (inclusive), return true if there exists an original string
# that could be encoded as both s1 and s2. Otherwise, return false.
#
# Note: The test cases are generated such that the number of consecutive digits
# in s1 and s2 does not exceed 3.
#
#
#
# Example 1:
#
# Input: s1 = "internationalization", s2 = "i18n"
# Output: true
# Explanation: It is possible that "internationalization" was the original
# string.
# - "internationalization"
#   -> Split:       ["internationalization"]
#   -> Do not replace any element
#   -> Concatenate:  "internationalization", which is s1.
# - "internationalization"
#   -> Split:       ["i", "nternationalizatio", "n"]
#   -> Replace:     ["i", "18",                 "n"]
#   -> Concatenate:  "i18n", which is s2
#
# Example 2:
#
# Input: s1 = "l123e", s2 = "44"
# Output: true
# Explanation: It is possible that "leetcode" was the original string.
# - "leetcode"
#   -> Split:      ["l", "e", "et", "cod", "e"]
#   -> Replace:    ["l", "1", "2",  "3",   "e"]
#   -> Concatenate: "l123e", which is s1.
# - "leetcode"
#   -> Split:      ["leet", "code"]
#   -> Replace:    ["4",    "4"]
#   -> Concatenate: "44", which is s2.
#
# Example 3:
#
# Input: s1 = "a5b", s2 = "c5b"
# Output: false
# Explanation: It is impossible.
# - The original string encoded as s1 must start with the letter 'a'.
# - The original string encoded as s2 must start with the letter 'c'.
#
#
#
# Constraints:
#
#
# 1 <= s1.length, s2.length <= 40
#
#
# s1 and s2 consist of digits 1-9 (inclusive), and lowercase English letters
# only.
#
#
# The number of consecutive digits in s1 and s2 does not exceed 3.
#

# @lc code=start
from functools import lru_cache


class Solution:
    def possiblyEquals(self, s1: str, s2: str) -> bool:
        """
        Interview explanation:
        Encoded strings mix letters and digit runs (length shortcuts 1..999).
        Ask whether some original string can decode to both encodings.

        Algorithm:
        - diff = length s1 is ahead of s2. Process digits into possible lengths;
          match letters when diff==0; consume length when one side leads.

        Complexity: O(|s1|*|s2|*diffRange) with pruning; |si|≤40.
        """
        n1, n2 = len(s1), len(s2)

        def parse_lens(s: str, i: int):
            # return list of (new_index, possible_lengths) for digit run starting at i
            vals = []
            num = 0
            for j in range(i, min(i + 3, len(s))):
                if not s[j].isdigit():
                    break
                num = num * 10 + int(s[j])
                vals.append((j + 1, num))
            return vals

        @lru_cache(None)
        def dfs(i: int, j: int, diff: int) -> bool:
            if i == n1 and j == n2:
                return diff == 0
            if i < n1 and s1[i].isdigit():
                for ni, val in parse_lens(s1, i):
                    if dfs(ni, j, diff + val):
                        return True
                return False
            if j < n2 and s2[j].isdigit():
                for nj, val in parse_lens(s2, j):
                    if dfs(i, nj, diff - val):
                        return True
                return False
            if diff > 0:
                if j == n2:
                    return False
                return dfs(i, j + 1, diff - 1)
            if diff < 0:
                if i == n1:
                    return False
                return dfs(i + 1, j, diff + 1)
            # diff == 0: match letters
            if i == n1 or j == n2:
                return False
            if s1[i] != s2[j]:
                return False
            return dfs(i + 1, j + 1, 0)

        return dfs(0, 0, 0)
# @lc code=end
