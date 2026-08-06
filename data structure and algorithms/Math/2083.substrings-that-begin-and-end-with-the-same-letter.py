#
# @lc app=leetcode id=2083 lang=python3
#
# [2083] Substrings That Begin and End With the Same Letter
#
# https://leetcode.com/problems/substrings-that-begin-and-end-with-the-same-letter/description/
#
# algorithms
# Medium (74.44%)
# Likes:    137
# Dislikes: 12
# Total Accepted:    14.1K
# Total Submissions: 19K
# Testcase Example:  "\"abcba\""
#
#
# You are given a 0-indexed string s consisting of only lowercase English
# letters. Return the number of substrings in s that begin and end with
# the same character.
#
# A substring is a contiguous non-empty sequence of characters within a
# string.
#
# Example 1:
#
# Input: s = "abcba"
# Output: 7
# Explanation:
# The substrings of length 1 that start and end with the same letter are:
# "a", "b", "c", "b", and "a".
# The substring of length 3 that starts and ends with the same letter is:
# "bcb".
# The substring of length 5 that starts and ends with the same letter is:
# "abcba".
#
# Example 2:
#
# Input: s = "abacad"
# Output: 9
# Explanation:
# The substrings of length 1 that start and end with the same letter are:
# "a", "b", "a", "c", "a", and "d".
# The substrings of length 3 that start and end with the same letter are:
# "aba" and "aca".
# The substring of length 5 that starts and ends with the same letter is:
# "abaca".
#
# Example 3:
#
# Input: s = "a"
# Output: 1
# Explanation:
# The substring of length 1 that starts and ends with the same letter is:
# "a".
#
# Constraints:
#
# 1 <= s.length <= 10^5
#
# s consists only of lowercase English letters.
#
# @lc code=start
from collections import Counter


class Solution:
    def numberOfSubstrings(self, s: str) -> int:
        """
        Interview explanation:
        Premium. Count substrings that start and end with the same letter
        (including length-1).

        Algorithm:
        - For a char with frequency f, choose any two occurrences as ends:
          f*(f+1)/2 substrings.

        Complexity: O(n) time, O(1) space.
        """
        cnt = Counter(s)
        return sum(f * (f + 1) // 2 for f in cnt.values())

    def numberOfSubstrings_prefix(self, s: str) -> int:
        """
        Interview explanation:
        Alternate running count: when seeing char c, it ends (seen[c]+1)
        substrings that start with c.

        Algorithm:
        - Maintain frequency so far; ans += ++freq[c].

        Complexity: O(n) time, O(1) space.
        """
        freq = Counter()
        ans = 0
        for ch in s:
            freq[ch] += 1
            ans += freq[ch]
        return ans
# @lc code=end
