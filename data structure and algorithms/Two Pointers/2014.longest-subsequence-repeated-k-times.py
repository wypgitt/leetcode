#
# @lc app=leetcode id=2014 lang=python3
#
# [2014] Longest Subsequence Repeated k Times
#
# https://leetcode.com/problems/longest-subsequence-repeated-k-times/description/
#
# algorithms
# Hard (70.93%)
# Likes:    838
# Dislikes: 117
# Total Accepted:    74.7K
# Total Submissions: 105.4K
# Testcase Example:  "\"letsleetcode\"\n2"
#
# You are given a string s of length n, and an integer k. You are tasked to find
# the longest subsequence repeated k times in string s.
#
# A subsequence is a string that can be derived from another string by deleting
# some or no characters without changing the order of the remaining characters.
#
# A subsequence seq is repeated k times in the string s if seq * k is a
# subsequence of s, where seq * k represents a string constructed by
# concatenating seq k times.
#
#
# For example, "bba" is repeated 2 times in the string "bababcba", because the
# string "bbabba", constructed by concatenating "bba" 2 times, is a subsequence
# of the string "bababcba".
#
# Return the longest subsequence repeated k times in string s. If multiple such
# subsequences are found, return the lexicographically largest one. If there is
# no such subsequence, return an empty string.
#
#
#
# Example 1:
#
# Input: s = "letsleetcode", k = 2
# Output: "let"
# Explanation: There are two longest subsequences repeated 2 times: "let" and
# "ete".
# "let" is the lexicographically largest one.
#
# Example 2:
#
# Input: s = "bb", k = 2
# Output: "b"
# Explanation: The longest subsequence repeated 2 times is "b".
#
# Example 3:
#
# Input: s = "ab", k = 2
# Output: ""
# Explanation: There is no subsequence repeated 2 times. Empty string is
# returned.
#
#
#
# Constraints:
#
#
# n == s.length
#
#
# 2 <= k <= 2000
#
#
# 2 <= n < min(2001, k * 8)
#
#
# s consists of lowercase English letters.
#

# @lc code=start
from collections import Counter, deque


class Solution:
    def longestSubsequenceRepeatedK(self, s: str, k: int) -> str:
        """
        Interview explanation:
        Longest subsequence that appears as a subsequence at least k times;
        ties broken by lexicographically largest. Answer length <= n/k.

        Algorithm:
        - Candidate chars with freq >= k, sorted ascending so last BFS string is lex-largest.
        - BFS grow strings; keep if t*k is a subsequence of s; last is best.

        Complexity: O(|cand|^L * n) with L small; O(|cand|^L) space.
        """
        freq = Counter(s)
        cand = sorted(c for c, v in freq.items() if v >= k)

        def ok(t: str) -> bool:
            need = t * k
            i = 0
            for ch in s:
                if ch == need[i]:
                    i += 1
                    if i == len(need):
                        return True
            return False

        best = ''
        q = deque([''])
        while q:
            cur = q.popleft()
            for c in cand:
                nxt = cur + c
                if ok(nxt):
                    best = nxt
                    q.append(nxt)
        return best
# @lc code=end
