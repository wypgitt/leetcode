#
# @lc app=leetcode id=3297 lang=python3
#
# [3297] Count Substrings That Can Be Rearranged to Contain a String I
#
# https://leetcode.com/problems/count-substrings-that-can-be-rearranged-to-contain-a-string-i/description/
#
# algorithms
# Medium (43.49%)
# Likes:    126
# Dislikes: 27
# Total Accepted:    20.7K
# Total Submissions: 47.6K
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
# 1 <= word1.length <= 10^5
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
        A substring is valid if its multiset covers word2 (can rearrange to
        put word2 as a prefix). Count such substrings of word1.

        Algorithm:
        - Sliding window maintaining coverage of need = Counter(word2).
        - Shrink left while the window still covers; then all starts < left work.
        - ans += left for each right endpoint.

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
