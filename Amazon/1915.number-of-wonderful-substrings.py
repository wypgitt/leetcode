#
# @lc app=leetcode id=1915 lang=python3
#
# [1915] Number of Wonderful Substrings
#
# https://leetcode.com/problems/number-of-wonderful-substrings/description/
#
# algorithms
# Medium (66.57%)
# Likes:    1846
# Dislikes: 284
# Total Accepted:    91.8K
# Total Submissions: 138K
# Testcase Example:  "\"aba\""
#
# A wonderful string is a string where at most one letter appears an odd number
# of times.
#
# For example, "ccjjc" and "abab" are wonderful, but "ab" is not.
#
# Given a string word that consists of the first ten lowercase English letters
# ('a' through 'j'), return the number of wonderful non-empty substrings in
# word. If the same substring appears multiple times in word, then count each
# occurrence separately.
#
# A substring is a contiguous sequence of characters in a string.
#
# Example 1:
#
# Input: word = "aba"
# Output: 4
# Explanation: The four wonderful substrings are underlined below:
# - "aba" -> "a"
# - "aba" -> "b"
# - "aba" -> "a"
# - "aba" -> "aba"
#
# Example 2:
#
# Input: word = "aabb"
# Output: 9
# Explanation: The nine wonderful substrings are underlined below:
# - "aabb" -> "a"
# - "aabb" -> "aa"
# - "aabb" -> "aab"
# - "aabb" -> "aabb"
# - "aabb" -> "a"
# - "aabb" -> "abb"
# - "aabb" -> "b"
# - "aabb" -> "bb"
# - "aabb" -> "b"
#
# Example 3:
#
# Input: word = "he"
# Output: 2
# Explanation: The two wonderful substrings are underlined below:
# - "he" -> "h"
# - "he" -> "e"
#
# Constraints:
#
# 1 <= word.length <= 10^5
#
# word consists of lowercase English letters from 'a' to 'j'.
#

# @lc code=start
class Solution:
    def wonderfulSubstrings(self, word: str) -> int:
        """
        Interview explanation:
        Wonderful = at most one char with odd count in substring. Letters a-j →
        10-bit mask. Prefix XOR; for each prefix, add counts of same mask
        (all even) and masks differing by 1 bit (one odd).

        Algorithm:
        - freq[0]=1; mask=0; for each char flip bit; ans += freq[mask] + sum
          freq[mask^(1<<b)]; freq[mask]++.

        Complexity: O(n * 10) time, O(2^10) space.
        """
        freq = [0] * 1024
        freq[0] = 1
        mask = ans = 0
        for ch in word:
            mask ^= 1 << (ord(ch) - ord("a"))
            ans += freq[mask]
            for b in range(10):
                ans += freq[mask ^ (1 << b)]
            freq[mask] += 1
        return ans
# @lc code=end
