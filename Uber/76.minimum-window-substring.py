#
# @lc app=leetcode id=76 lang=python3
#
# [76] Minimum Window Substring
#
# https://leetcode.com/problems/minimum-window-substring/description/
#
# algorithms
# Hard (48.16%)
# Likes:    20519
# Dislikes: 862
# Total Accepted:    2.3M
# Total Submissions: 4.8M
# Testcase Example:  "\"ADOBECODEBANC\""
#
# Given two strings s and t of lengths m and n respectively, return the minimum
# window substring of s such that every character in t (including duplicates)
# is included in the window. If there is no such substring, return the empty
# string "".
#
# The testcases will be generated such that the answer is unique.
#
# Example 1:
#
# Input: s = "ADOBECODEBANC", t = "ABC"
# Output: "BANC"
# Explanation: The minimum window substring "BANC" includes 'A', 'B', and 'C'
# from string t.
#
# Example 2:
#
# Input: s = "a", t = "a"
# Output: "a"
# Explanation: The entire string s is the minimum window.
#
# Example 3:
#
# Input: s = "a", t = "aa"
# Output: ""
# Explanation: Both 'a's from t must be included in the window.
# Since the largest window of s only has one 'a', return empty string.
#
# Constraints:
#
# m == s.length
#
# n == t.length
#
# 1 <= m, n <= 10^5
#
# s and t consist of uppercase and lowercase English letters.
#
# Follow up: Could you find an algorithm that runs in O(m + n) time?
#

# @lc code=start
from collections import Counter


class Solution:
    def minWindow(self, s: str, t: str) -> str:
        """
        Interview explanation:
        Sliding window: expand right until the window covers all of t's
        multiset, then shrink left to minimize while still valid.

        Algorithm:
        - need = Counter(t); missing = number of distinct chars still owed.
        - Expand right; decrement need[c]; when need[c] hits 0, missing--.
        - While missing == 0, update best window and release s[left].
        - Return the smallest covering substring (or "").

        Complexity: O(m + n) time, O(σ) space for character counts.
        """
        if not t or not s or len(t) > len(s):
            return ""

        need = Counter(t)
        missing = len(need)
        best_len = float("inf")
        best_start = 0
        left = 0

        for right, ch in enumerate(s):
            if ch in need:
                need[ch] -= 1
                if need[ch] == 0:
                    missing -= 1

            while missing == 0:
                if right - left + 1 < best_len:
                    best_len = right - left + 1
                    best_start = left

                left_ch = s[left]
                if left_ch in need:
                    need[left_ch] += 1
                    if need[left_ch] > 0:
                        missing += 1
                left += 1

        return "" if best_len == float("inf") else s[best_start : best_start + best_len]
# @lc code=end
