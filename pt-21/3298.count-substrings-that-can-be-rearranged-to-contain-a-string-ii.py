#
# @lc app=leetcode id=3298 lang=python3
#
# [3298] Count Substrings That Can Be Rearranged to Contain a String II
#
# https://leetcode.com/problems/count-substrings-that-can-be-rearranged-to-contain-a-string-ii/description/
#
# algorithms
# Hard (56.43%)
# Likes:    91
# Dislikes: 7
# Total Accepted:    18K
# Total Submissions: 31.9K
# Testcase Example:  "\"bcca\"\n\"abc\""
#
#
# You are given two strings word1 and word2.
#
# A string x is called valid if x can be rearranged to have word2 as a
# prefix.
#
# Return the total number of valid substrings of word1.
#
# Note that the memory limits in this problem are smaller than usual, so
# you must implement a solution with a linear runtime complexity.
#
# Example 1:
#
# Input: word1 = "bcca", word2 = "abc"
#
# Output: 1
#
# Explanation:
#
# The only valid substring is "bcca" which can be rearranged to "abcc"
# having "abc" as a prefix.
#
# Example 2:
#
# Input: word1 = "abcabc", word2 = "abc"
#
# Output: 10
#
# Explanation:
#
# All the substrings except substrings of size 1 and size 2 are valid.
#
# Example 3:
#
# Input: word1 = "abcabc", word2 = "aaabc"
#
# Output: 0
#
# Constraints:
#
# 1 <= word1.length <= 10^6
#
# 1 <= word2.length <= 10^4
#
# word1 and word2 consist only of lowercase English letters.
#

# @lc code=start
from collections import Counter


class Solution:
    def validSubstringCount(self, word1: str, word2: str) -> int:
        """
        Interview explanation:
        Same covering-substring count as I, with |word1| up to 1e6 — must be
        linear sliding window (no heavy per-window rebuilds).

        Algorithm:
        - Counter need for word2; expand right, shrink left while covered.
        - For each right, add left (starts 0..left-1 all remain covering).

        Complexity: O(|word1| + |word2|) time, O(1) space over alphabet.
        """
        need = Counter(word2)
        required = len(need)
        have = 0
        window: Counter = Counter()
        left = 0
        ans = 0
        for right, ch in enumerate(word1):
            window[ch] += 1
            if ch in need and window[ch] == need[ch]:
                have += 1
            while have == required:
                c = word1[left]
                if c in need and window[c] == need[c]:
                    have -= 1
                window[c] -= 1
                left += 1
            ans += left
        return ans
# @lc code=end
