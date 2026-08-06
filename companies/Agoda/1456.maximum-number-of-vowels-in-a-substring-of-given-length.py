#
# @lc app=leetcode id=1456 lang=python3
#
# [1456] Maximum Number of Vowels in a Substring of Given Length
#
# https://leetcode.com/problems/maximum-number-of-vowels-in-a-substring-of-given-length/description/
#
# algorithms
# Medium (62.59%)
# Likes:    4012
# Dislikes: 153
# Total Accepted:    756K
# Total Submissions: 1.2M
# Testcase Example:  "\"abciiidef\""
#
# Given a string s and an integer k, return the maximum number of vowel letters
# in any substring of s with length k.
#
# Vowel letters in English are 'a', 'e', 'i', 'o', and 'u'.
#
# Example 1:
#
# Input: s = "abciiidef", k = 3
# Output: 3
# Explanation: The substring "iii" contains 3 vowel letters.
#
# Example 2:
#
# Input: s = "aeiou", k = 2
# Output: 2
# Explanation: Any substring of length 2 contains 2 vowels.
#
# Example 3:
#
# Input: s = "leetcode", k = 3
# Output: 2
# Explanation: "lee", "eet" and "ode" contain 2 vowels.
#
# Constraints:
#
# 1 <= s.length <= 10^5
#
# s consists of lowercase English letters.
#
# 1 <= k <= s.length
#

# @lc code=start
class Solution:
    def maxVowels(self, s: str, k: int) -> int:
        """
        Interview explanation:
        Max vowels in any substring of length k — classic fixed sliding window.

        Algorithm:
        - Count vowels in first k; slide: add s[i], remove s[i-k]; track max.

        Complexity: O(n) time, O(1) space.
        """
        vowels = set("aeiou")
        cur = sum(1 for c in s[:k] if c in vowels)
        best = cur
        for i in range(k, len(s)):
            if s[i] in vowels:
                cur += 1
            if s[i - k] in vowels:
                cur -= 1
            best = max(best, cur)
        return best

    def maxVowels_prefix(self, s: str, k: int) -> int:
        """
        Interview explanation:
        Alternate: prefix vowel counts; window sum = pref[i]-pref[i-k].

        Algorithm:
        - Build pref; max over i of pref[i]-pref[i-k].

        Complexity: O(n) time, O(n) space.
        """
        vowels = set("aeiou")
        n = len(s)
        pref = [0] * (n + 1)
        for i, c in enumerate(s):
            pref[i + 1] = pref[i] + (c in vowels)
        return max(pref[i] - pref[i - k] for i in range(k, n + 1))
# @lc code=end
