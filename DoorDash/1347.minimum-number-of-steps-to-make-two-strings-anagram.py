#
# @lc app=leetcode id=1347 lang=python3
#
# [1347] Minimum Number of Steps to Make Two Strings Anagram
#
# https://leetcode.com/problems/minimum-number-of-steps-to-make-two-strings-anagram/description/
#
# algorithms
# Medium (82.57%)
# Likes:    2834
# Dislikes: 122
# Total Accepted:    343K
# Total Submissions: 415K
# Testcase Example:  "\"bab\""
#
# You are given two strings of the same length s and t. In one step you can
# choose any character of t and replace it with another character.
#
# Return the minimum number of steps to make t an anagram of s.
#
# An Anagram of a string is a string that contains the same characters with a
# different (or the same) ordering.
#
# Example 1:
#
# Input: s = "bab", t = "aba"
# Output: 1
# Explanation: Replace the first 'a' in t with b, t = "bba" which is anagram of
# s.
#
# Example 2:
#
# Input: s = "leetcode", t = "practice"
# Output: 5
# Explanation: Replace 'p', 'r', 'a', 'i' and 'c' from t with proper characters
# to make t anagram of s.
#
# Example 3:
#
# Input: s = "anagram", t = "mangaar"
# Output: 0
# Explanation: "anagram" and "mangaar" are anagrams.
#
# Constraints:
#
# 1 <= s.length <= 5 * 10^4
#
# s.length == t.length
#
# s and t consist of lowercase English letters only.
#

# @lc code=start
from collections import Counter


class Solution:
    def minSteps(self, s: str, t: str) -> int:
        """
        Interview explanation:
        Replace chars in t so t becomes anagram of s. Steps = sum of positive
        count deficits = half L1 distance of frequency vectors =
        sum max(cnt_s - cnt_t, 0).

        Algorithm:
        - Count both; sum positive differences.

        Complexity: O(n) time, O(1) space (26 letters).
        """
        cs, ct = Counter(s), Counter(t)
        return sum(max(cs[c] - ct[c], 0) for c in cs)
# @lc code=end

