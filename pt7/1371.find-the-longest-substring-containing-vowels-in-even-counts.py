#
# @lc app=leetcode id=1371 lang=python3
#
# [1371] Find the Longest Substring Containing Vowels in Even Counts
#
# https://leetcode.com/problems/find-the-longest-substring-containing-vowels-in-even-counts/description/
#
# algorithms
# Medium (75.60%)
# Likes:    2568
# Dislikes: 142
# Total Accepted:    141.6K
# Total Submissions: 187.3K
# Testcase Example:  '"eleetminicoworoep"'
#
# Given the string s, return the size of the longest substring containing each
# vowel an even number of times. That is, 'a', 'e', 'i', 'o', and 'u' must
# appear an even number of times.
# 
# 
# Example 1:
# 
# 
# Input: s = "eleetminicoworoep"
# Output: 13
# Explanation: The longest substring is "leetminicowor" which contains two each
# of the vowels: e, i and o and zero of the vowels: a and u.
# 
# 
# Example 2:
# 
# 
# Input: s = "leetcodeisgreat"
# Output: 5
# Explanation: The longest substring is "leetc" which contains two e's.
# 
# 
# Example 3:
# 
# 
# Input: s = "bcbcbc"
# Output: 6
# Explanation: In this case, the given string "bcbcbc" is the longest because
# all vowels: a, e, i, o and u appear zero times.
# 
# 
# 
# Constraints:
# 
# 
# 1 <= s.length <= 5 x 10^5
# s contains only lowercase English letters.
# 
# 
#

# @lc code=start
from __future__ import annotations


class Solution:
    def findTheLongestSubstring(self, s: str) -> int:
        bit_for_vowel = {"a": 0, "e": 1, "i": 2, "o": 3, "u": 4}
        first_seen = {0: -1}
        mask = 0
        best = 0

        for index, char in enumerate(s):
            if char in bit_for_vowel:
                mask ^= 1 << bit_for_vowel[char]

            if mask in first_seen:
                best = max(best, index - first_seen[mask])
            else:
                first_seen[mask] = index

        return best
# @lc code=end

#
# Interview explanation
# ---------------------
# Idea:
# We only care whether each vowel count is even or odd. Represent the parity of
# the five vowels with a 5-bit mask. If the same mask appears at two indices,
# the substring between them has even counts for every vowel.
#
# Data structure:
# `first_seen[mask]` stores the earliest index where that parity mask appeared.
# Keeping the earliest index maximizes future substring length.
#
# Walkthrough:
# 1. Start with mask 0 at index -1, meaning all vowel counts are even before the
#    string begins.
# 2. When reading a vowel, flip its bit with XOR.
# 3. If this mask was seen before, the substring after that first index through
#    the current index has all even vowel counts.
# 4. Otherwise, store this index as the first occurrence of the mask.
#
# Edge cases:
# - No vowels: mask stays 0, answer becomes the whole string.
# - Single vowel: no even substring including it unless paired later.
# - Mixed consonants: consonants do not affect the mask.
#
# Complexity:
# - Time: O(n).
# - Space: O(1), at most 32 masks.
