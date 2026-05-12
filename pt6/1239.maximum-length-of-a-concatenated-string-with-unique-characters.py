#
# @lc app=leetcode id=1239 lang=python3
#
# [1239] Maximum Length of a Concatenated String with Unique Characters
#
# https://leetcode.com/problems/maximum-length-of-a-concatenated-string-with-unique-characters/description/
#
# algorithms
# Medium (54.74%)
# Likes:    4573
# Dislikes: 340
# Total Accepted:    325.5K
# Total Submissions: 594.5K
# Testcase Example:  '["un","iq","ue"]'
#
# You are given an array of strings arr. A string s is formed by the
# concatenation of a subsequence of arr that has unique characters.
# 
# Return the maximum possible length of s.
# 
# A subsequence is an array that can be derived from another array by deleting
# some or no elements without changing the order of the remaining elements.
# 
# 
# Example 1:
# 
# 
# Input: arr = ["un","iq","ue"]
# Output: 4
# Explanation: All the valid concatenations are:
# - ""
# - "un"
# - "iq"
# - "ue"
# - "uniq" ("un" + "iq")
# - "ique" ("iq" + "ue")
# Maximum length is 4.
# 
# 
# Example 2:
# 
# 
# Input: arr = ["cha","r","act","ers"]
# Output: 6
# Explanation: Possible longest valid concatenations are "chaers" ("cha" +
# "ers") and "acters" ("act" + "ers").
# 
# 
# Example 3:
# 
# 
# Input: arr = ["abcdefghijklmnopqrstuvwxyz"]
# Output: 26
# Explanation: The only string in arr has all 26 characters.
# 
# 
# 
# Constraints:
# 
# 
# 1 <= arr.length <= 16
# 1 <= arr[i].length <= 26
# arr[i] contains only lowercase English letters.
# 
# 
#

# @lc code=start
from typing import List


class Solution:
    def maxLength(self, arr: List[str]) -> int:
        masks = [0]
        best = 0

        for word in arr:
            mask = 0
            valid = True
            for ch in word:
                bit = 1 << (ord(ch) - ord("a"))
                if mask & bit:
                    valid = False
                    break
                mask |= bit
            if not valid:
                continue

            for existing in masks[:]:
                if existing & mask == 0:
                    combined = existing | mask
                    masks.append(combined)
                    best = max(best, combined.bit_count())

        return best
# @lc code=end

# Explanation
# -----------
# Represent each valid word as a 26-bit mask. A word with duplicate letters is
# skipped because it can never appear in a valid concatenation. Maintain all
# masks that can be built from processed words; a new word can combine with an
# existing mask only if their bitwise AND is zero.
#
# Bit masks are the right data structure because uniqueness and overlap checks
# become constant-time integer operations instead of repeated set scans.
#
# The DP list starts with mask 0 for the empty concatenation. Iterating over a
# snapshot of existing masks prevents using the same word twice.
#
# Edge cases: empty answer when every word has duplicates; words with shared
# letters; maximum length is count of set bits in the combined mask.
#
# Time complexity: O(n * 2^n) in the worst case.
# Space complexity: O(2^n) masks.
