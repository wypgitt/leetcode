#
# @lc app=leetcode id=28 lang=python3
#
# [28] Find the Index of the First Occurrence in a String
#
# https://leetcode.com/problems/find-the-index-of-the-first-occurrence-in-a-string/description/
#
# algorithms
# Easy (47.11%)
# Likes:    7776
# Dislikes: 592
# Total Accepted:    4.3M
# Total Submissions: 9.1M
# Testcase Example:  "\"sadbutsad\""
#
# Given two strings needle and haystack, return the index of the first
# occurrence of needle in haystack, or -1 if needle is not part of haystack.
#
# Example 1:
#
# Input: haystack = "sadbutsad", needle = "sad"
# Output: 0
# Explanation: "sad" occurs at index 0 and 6.
# The first occurrence is at index 0, so we return 0.
#
# Example 2:
#
# Input: haystack = "leetcode", needle = "leeto"
# Output: -1
# Explanation: "leeto" did not occur in "leetcode", so we return -1.
#
# Constraints:
#
# 1 <= haystack.length, needle.length <= 10^4
#
# haystack and needle consist of only lowercase English characters.
#

# @lc code=start
class Solution:
    def strStr(self, haystack: str, needle: str) -> int:
        """
        Interview explanation:
        Classic substring search via KMP: find the first index where `needle`
        occurs inside `haystack`, or -1 if absent. LPS jumps avoid restarting
        on every mismatch.

        Algorithm:
        - Build the LPS (longest proper prefix which is also suffix) array for
          `needle` in O(m).
        - Scan `haystack` with pointer i and `needle` with pointer j.
        - On mismatch, jump j using LPS instead of restarting from 0.
        - When j == m, return i - m.

        Complexity: O(n + m) time, O(m) space.
        """
        n, m = len(haystack), len(needle)
        if m == 0:
            return 0
        if m > n:
            return -1

        lps = [0] * m
        length = 0
        i = 1
        while i < m:
            if needle[i] == needle[length]:
                length += 1
                lps[i] = length
                i += 1
            elif length:
                length = lps[length - 1]
            else:
                lps[i] = 0
                i += 1

        i = j = 0
        while i < n:
            if haystack[i] == needle[j]:
                i += 1
                j += 1
                if j == m:
                    return i - m
            elif j:
                j = lps[j - 1]
            else:
                i += 1
        return -1

    def strStrSliding(self, haystack: str, needle: str) -> int:
        """
        Interview explanation:
        Sliding-window substring search: compare each haystack window of length
        m against needle. Simple for interviews when n, m are small.

        Algorithm:
        - For each start index i in [0, n - m], compare haystack[i:i+m] with
          needle.
        - Return the first matching i, or -1 if none.

        Complexity: O((n - m + 1) * m) time worst case, O(1) space.
        """
        n, m = len(haystack), len(needle)
        if m == 0:
            return 0
        if m > n:
            return -1

        for i in range(n - m + 1):
            if haystack[i : i + m] == needle:
                return i
        return -1
# @lc code=end
