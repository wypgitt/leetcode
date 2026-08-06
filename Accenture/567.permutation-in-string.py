#
# @lc app=leetcode id=567 lang=python3
#
# [567] Permutation in String
#
# https://leetcode.com/problems/permutation-in-string/description/
#
# algorithms
# Medium (49.43%)
# Likes:    13191
# Dislikes: 526
# Total Accepted:    1.6M
# Total Submissions: 3.2M
# Testcase Example:  "\"ab\""
#
# Given two strings s1 and s2, return true if s2 contains a permutation of s1,
# or false otherwise.
#
# In other words, return true if one of s1's permutations is the substring of
# s2.
#
# Example 1:
#
# Input: s1 = "ab", s2 = "eidbaooo"
# Output: true
# Explanation: s2 contains one permutation of s1 ("ba").
#
# Example 2:
#
# Input: s1 = "ab", s2 = "eidboaoo"
# Output: false
#
# Constraints:
#
# 1 <= s1.length, s2.length <= 10^4
#
# s1 and s2 consist of lowercase English letters.
#


# @lc code=start
from collections import Counter


class Solution:
    def checkInclusion(self, s1: str, s2: str) -> bool:
        """
        Interview explanation:
        A permutation of s1 is any window of length len(s1) with the same
        character multiset. Maintain a fixed-length sliding window over s2 and
        compare frequency maps (or a diff counter + match count).

        Algorithm:
        - need = Counter(s1); window over s2 of size len(s1).
        - Slide: add right char, remove left char; succeed when window == need.

        Complexity: O(|s2|) time with O(1) alphabet work, O(Σ) space (26 letters).
        """
        n, m = len(s1), len(s2)
        if n > m:
            return False
        need = Counter(s1)
        window = Counter(s2[:n])
        if window == need:
            return True
        for i in range(n, m):
            window[s2[i]] += 1
            left = s2[i - n]
            window[left] -= 1
            if window[left] == 0:
                del window[left]
            if window == need:
                return True
        return False

    def checkInclusionArray(self, s1: str, s2: str) -> bool:
        """
        Interview explanation:
        Same sliding window, but use int[26] arrays and a running "matches"
        count of how many letters currently have the required frequency —
        avoids rebuilding/comparing full maps each step.

        Algorithm:
        - Build need[26]; maintain have[26] and matches (# letters with have==need).
        - Slide fixed window; update matches when a letter's count hits/leaves need.

        Complexity: O(|s2|) time, O(1) space.
        """
        n, m = len(s1), len(s2)
        if n > m:
            return False
        need = [0] * 26
        have = [0] * 26
        for ch in s1:
            need[ord(ch) - 97] += 1
        matches = sum(1 for i in range(26) if need[i] == 0)
        for i, ch in enumerate(s2):
            idx = ord(ch) - 97
            have[idx] += 1
            if have[idx] == need[idx]:
                matches += 1
            elif have[idx] == need[idx] + 1:
                matches -= 1
            if i >= n:
                left = ord(s2[i - n]) - 97
                if have[left] == need[left]:
                    matches -= 1
                elif have[left] == need[left] + 1:
                    matches += 1
                have[left] -= 1
            if matches == 26:
                return True
        return False
# @lc code=end

