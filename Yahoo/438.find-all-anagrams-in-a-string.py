#
# @lc app=leetcode id=438 lang=python3
#
# [438] Find All Anagrams in a String
#
# https://leetcode.com/problems/find-all-anagrams-in-a-string/description/
#
# algorithms
# Medium (54.25%)
# Likes:    13357
# Dislikes: 382
# Total Accepted:    1.3M
# Total Submissions: 2.3M
# Testcase Example:  "\"cbaebabacd\""
#
# Given two strings s and p, return an array of all the start indices of p's
# anagrams in s. You may return the answer in any order.
#
# Example 1:
#
# Input: s = "cbaebabacd", p = "abc"
# Output: [0,6]
# Explanation:
# The substring with start index = 0 is "cba", which is an anagram of "abc".
# The substring with start index = 6 is "bac", which is an anagram of "abc".
#
# Example 2:
#
# Input: s = "abab", p = "ab"
# Output: [0,1,2]
# Explanation:
# The substring with start index = 0 is "ab", which is an anagram of "ab".
# The substring with start index = 1 is "ba", which is an anagram of "ab".
# The substring with start index = 2 is "ab", which is an anagram of "ab".
#
# Constraints:
#
# 1 <= s.length, p.length <= 3 * 10^4
#
# s and p consist of lowercase English letters.
#

# @lc code=start

from typing import List


class Solution:
    def findAnagrams(self, s: str, p: str) -> List[int]:
        """
        Interview explanation:
        Fixed-size sliding window with character counts. Window of len(p) is an
        anagram when its frequency vector matches p's.

        Algorithm:
        - need counts for p; maintain window counts and matched unique-char count.
        - Expand right; shrink when window > len(p); record left when equal.

        Complexity: O(n) time, O(1) space (26 letters).
        """
        if len(p) > len(s):
            return []
        need = [0] * 26
        window = [0] * 26
        for ch in p:
            need[ord(ch) - 97] += 1
        required = sum(1 for c in need if c > 0)
        formed = 0
        ans = []
        left = 0
        for right, ch in enumerate(s):
            idx = ord(ch) - 97
            window[idx] += 1
            if need[idx] and window[idx] == need[idx]:
                formed += 1
            if right - left + 1 > len(p):
                lidx = ord(s[left]) - 97
                if need[lidx] and window[lidx] == need[lidx]:
                    formed -= 1
                window[lidx] -= 1
                left += 1
            if right - left + 1 == len(p) and formed == required:
                ans.append(left)
        return ans
# @lc code=end
