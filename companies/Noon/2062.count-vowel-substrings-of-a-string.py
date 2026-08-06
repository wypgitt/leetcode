#
# @lc app=leetcode id=2062 lang=python3
#
# [2062] Count Vowel Substrings of a String
#
# https://leetcode.com/problems/count-vowel-substrings-of-a-string/description/
#
# algorithms
# Easy (73.36%)
# Likes:    1135
# Dislikes: 448
# Total Accepted:    82K
# Total Submissions: 111.7K
# Testcase Example:  "\"aeiouu\""
#
# A substring is a contiguous (non-empty) sequence of characters within a
# string.
#
# A vowel substring is a substring that only consists of vowels ('a', 'e', 'i',
# 'o', and 'u') and has all five vowels present in it.
#
# Given a string word, return the number of vowel substrings in word.
#
#
#
# Example 1:
#
# Input: word = "aeiouu"
# Output: 2
# Explanation: The vowel substrings of word are as follows (underlined):
# - "aeiouu"
# - "aeiouu"
#
# Example 2:
#
# Input: word = "unicornarihan"
# Output: 0
# Explanation: Not all 5 vowels are present, so there are no vowel substrings.
#
# Example 3:
#
# Input: word = "cuaieuouac"
# Output: 7
# Explanation: The vowel substrings of word are as follows (underlined):
# - "cuaieuouac"
# - "cuaieuouac"
# - "cuaieuouac"
# - "cuaieuouac"
# - "cuaieuouac"
# - "cuaieuouac"
# - "cuaieuouac"
#
#
#
# Constraints:
#
#
# 1 <= word.length <= 100
#
#
# word consists of lowercase English letters only.
#

# @lc code=start
from collections import defaultdict


class Solution:
    def countVowelSubstrings(self, word: str) -> int:
        """
        Interview explanation:
        Count substrings that contain only vowels and include all 5 vowels
        a,e,i,o,u at least once.

        Algorithm:
        - Between consonants, count substrings with all 5 vowels via two
          windows (at-most-5 vs at-most-4 distinct vowels) or last-seen indices.

        Complexity: O(n) time, O(1) space.
        """
        vowels = set('aeiou')
        n = len(word)
        ans = 0

        def count_at_most(k: int, s: str) -> int:
            cnt = defaultdict(int)
            left = res = 0
            for right, ch in enumerate(s):
                cnt[ch] += 1
                while len(cnt) > k:
                    cnt[s[left]] -= 1
                    if cnt[s[left]] == 0:
                        del cnt[s[left]]
                    left += 1
                res += right - left + 1
            return res

        i = 0
        while i < n:
            if word[i] not in vowels:
                i += 1
                continue
            j = i
            while j < n and word[j] in vowels:
                j += 1
            seg = word[i:j]
            ans += count_at_most(5, seg) - count_at_most(4, seg)
            i = j
        return ans

    def countVowelSubstrings_last(self, word: str) -> int:
        """
        Interview explanation:
        Alternate: track last index of each vowel and last consonant; for each
        right endpoint, substrings ending there that contain all vowels start
        after last consonant and at/before min last-vowel index.

        Algorithm:
        - Maintain last[vowel]; ans += max(0, min(last)-last_consonant).

        Complexity: O(n) time, O(1) space.
        """
        vowels = 'aeiou'
        last = {v: -1 for v in vowels}
        last_cons = -1
        ans = 0
        for i, ch in enumerate(word):
            if ch in last:
                last[ch] = i
                ans += max(0, min(last.values()) - last_cons)
            else:
                last_cons = i
                for v in vowels:
                    last[v] = -1
        return ans
# @lc code=end
