#
# @lc app=leetcode id=2981 lang=python3
#
# [2981] Find Longest Special Substring That Occurs Thrice I
#
# https://leetcode.com/problems/find-longest-special-substring-that-occurs-thrice-i/description/
#
# algorithms
# Medium (61.85%)
# Likes:    742
# Dislikes: 75
# Total Accepted:    133.5K
# Total Submissions: 215.9K
# Testcase Example:  "\"aaaa\""
#
#
# You are given a string s that consists of lowercase English letters.
#
# A string is called special if it is made up of only a single character.
# For example, the string "abc" is not special, whereas the strings "ddd",
# "zz", and "f" are special.
#
# Return the length of the longest special substring of s which occurs at
# least thrice, or -1 if no special substring occurs at least thrice.
#
# A substring is a contiguous non-empty sequence of characters within a
# string.
#
# Example 1:
#
# Input: s = "aaaa"
# Output: 2
# Explanation: The longest special substring which occurs thrice is "aa":
# substrings "aaaa", "aaaa", and "aaaa".
# It can be shown that the maximum length achievable is 2.
#
# Example 2:
#
# Input: s = "abcdef"
# Output: -1
# Explanation: There exists no special substring which occurs at least
# thrice. Hence return -1.
#
# Example 3:
#
# Input: s = "abcaba"
# Output: 1
# Explanation: The longest special substring which occurs thrice is "a":
# substrings "abcaba", "abcaba", and "abcaba".
# It can be shown that the maximum length achievable is 1.
#
# Constraints:
#
# 3 <= s.length <= 50
#
# s consists of only lowercase English letters.
#

# @lc code=start
from collections import defaultdict


class Solution:
    def maximumLength(self, s: str) -> int:
        """
        Interview explanation:
        Special substring = run of one character. Find longest length that appears as a
        substring at least thrice (overlapping counts).

        Algorithm:
        - For each maximal run of length L of char c, substrings of length k appear
          (L-k+1) times from that run. Aggregate counts per (c, k); take max k with
          count >= 3.

        Complexity: O(n^2) time worst (n<=50), O(n) space.
        """
        n = len(s)
        freq: dict = defaultdict(int)
        i = 0
        while i < n:
            j = i
            while j < n and s[j] == s[i]:
                j += 1
            L = j - i
            c = s[i]
            for k in range(1, L + 1):
                freq[(c, k)] += L - k + 1
            i = j
        ans = -1
        for (_, k), cnt in freq.items():
            if cnt >= 3:
                ans = max(ans, k)
        return ans

    def maximumLength_brute(self, s: str) -> int:
        """
        Interview explanation:
        Alternate: enumerate all special substrings via nested loops; Counter frequencies.

        Algorithm:
        - For each start, extend while same char; count each s[i:i+len].

        Complexity: O(n^2) time, O(n^2) space.
        """
        from collections import Counter

        cnt: Counter = Counter()
        n = len(s)
        for i in range(n):
            for j in range(i, n):
                if s[j] != s[i]:
                    break
                cnt[s[i : j + 1]] += 1
        ans = -1
        for sub, c in cnt.items():
            if c >= 3:
                ans = max(ans, len(sub))
        return ans
# @lc code=end
