#
# @lc app=leetcode id=2953 lang=python3
#
# [2953] Count Complete Substrings
#
# https://leetcode.com/problems/count-complete-substrings/description/
#
# algorithms
# Hard (31.24%)
# Likes:    273
# Dislikes: 42
# Total Accepted:    12.1K
# Total Submissions: 38.7K
# Testcase Example:  "\"igigee\"\n2"
#
#
# You are given a string word and an integer k.
#
# A substring s of word is complete if:
#
# Each character in s occurs exactly k times.
#
# The difference between two adjacent characters is at most 2. That is,
# for any two adjacent characters c1 and c2 in s, the absolute difference
# in their positions in the alphabet is at most 2.
#
# Return the number of complete substrings of word.
#
# A substring is a non-empty contiguous sequence of characters in a
# string.
#
# Example 1:
#
# Input: word = "igigee", k = 2
# Output: 3
# Explanation: The complete substrings where each character appears
# exactly twice and the difference between adjacent characters is at most
# 2 are: igigee, igigee, igigee.
#
# Example 2:
#
# Input: word = "aaabbbccc", k = 3
# Output: 6
# Explanation: The complete substrings where each character appears
# exactly three times and the difference between adjacent characters is at
# most 2 are: aaabbbccc, aaabbbccc, aaabbbccc, aaabbbccc, aaabbbccc,
# aaabbbccc.
#
# Constraints:
#
# 1 <= word.length <= 10^5
#
# word consists only of lowercase English letters.
#
# 1 <= k <= word.length
#

# @lc code=start
from collections import Counter


class Solution:
    def countCompleteSubstrings(self, word: str, k: int) -> int:
        """
        Interview explanation:
        Complete: every distinct char appears exactly k times, and every
        adjacent pair differs by at most 2 in the alphabet.

        Algorithm:
        - Split word into maximal segments with adjacent |diff| <= 2.
        - In each segment, for unique-count u=1..26, slide windows of length
          u*k; accept when all freqs in the window are 0 or k (and exactly
          u chars present).

        Complexity: O(26 * n) time, O(1) space.
        """
        def count_in(seg: str) -> int:
            m = len(seg)
            total = 0
            for uniq in range(1, 27):
                length = uniq * k
                if length > m:
                    break
                cnt = Counter()
                bad = 0  # chars with count not in {0, k}

                def add(ch: str, delta: int) -> None:
                    nonlocal bad
                    prev = cnt[ch]
                    if prev and prev != k:
                        bad -= 1
                    cnt[ch] = prev + delta
                    cur = cnt[ch]
                    if cur == 0:
                        del cnt[ch]
                    elif cur != k:
                        bad += 1

                for i, ch in enumerate(seg):
                    add(ch, 1)
                    if i >= length:
                        add(seg[i - length], -1)
                    if i + 1 >= length and len(cnt) == uniq and bad == 0:
                        total += 1
            return total

        ans = 0
        n = len(word)
        start = 0
        for i in range(1, n + 1):
            if i == n or abs(ord(word[i]) - ord(word[i - 1])) > 2:
                ans += count_in(word[start:i])
                start = i
        return ans
# @lc code=end

