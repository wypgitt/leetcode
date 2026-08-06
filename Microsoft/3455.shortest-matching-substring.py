#
# @lc app=leetcode id=3455 lang=python3
#
# [3455] Shortest Matching Substring
#
# https://leetcode.com/problems/shortest-matching-substring/description/
#
# algorithms
# Hard (24.78%)
# Likes:    49
# Dislikes: 3
# Total Accepted:    6.9K
# Total Submissions: 27.7K
# Testcase Example:  "\"abaacbaecebce\"\n\"ba*c*ce\""
#
#
# You are given a string s and a pattern string p, where p contains
# exactly two '*' characters.
#
# The '*' in p matches any sequence of zero or more characters.
#
# Return the length of the shortest substring in s that matches p. If
# there is no such substring, return -1.
#
# Note: The empty substring is considered valid.
#
# Example 1:
#
# Input: s = "abaacbaecebce", p = "ba*c*ce"
#
# Output: 8
#
# Explanation:
#
# The shortest matching substring of p in s is "baecebce".
#
# Example 2:
#
# Input: s = "baccbaadbc", p = "cc*baa*adb"
#
# Output: -1
#
# Explanation:
#
# There is no matching substring in s.
#
# Example 3:
#
# Input: s = "a", p = "**"
#
# Output: 0
#
# Explanation:
#
# The empty substring is the shortest matching substring.
#
# Example 4:
#
# Input: s = "madlogic", p = "*adlogi*"
#
# Output: 6
#
# Explanation:
#
# The shortest matching substring of p in s is "adlogi".
#
# Constraints:
#
# 1 <= s.length <= 10^5
#
# 2 <= p.length <= 10^5
#
# s contains only lowercase English letters.
#
# p contains only lowercase English letters and exactly two '*'.
#

# @lc code=start

from bisect import bisect_left
from math import inf


class Solution:
    def shortestMatchingSubstring(self, s: str, p: str) -> int:
        """
        Interview explanation:
        Pattern is a*b*c (exactly two '*'). Match means find a, then b after a's
        end, then c after b's end; minimize end-start.

        Algorithm:
        - Split p into a,b,c. KMP-list all start positions (empty part matches every
          index). For each a-start, binary-search earliest b then c; track min length.

        Complexity: O(n + m) preprocess + O((occ_a) log n) queries.
        """
        a, b, c = p.split("*")

        def kmp_all(pat: str) -> list[int]:
            if not pat:
                return list(range(len(s) + 1))
            m = len(pat)
            lps = [0] * m
            j = 0
            for i in range(1, m):
                while j and pat[i] != pat[j]:
                    j = lps[j - 1]
                if pat[i] == pat[j]:
                    j += 1
                    lps[i] = j
            res: list[int] = []
            j = 0
            for i, ch in enumerate(s):
                while j and ch != pat[j]:
                    j = lps[j - 1]
                if ch == pat[j]:
                    j += 1
                    if j == m:
                        res.append(i - m + 1)
                        j = lps[j - 1]
            return res

        pos_a, pos_b, pos_c = kmp_all(a), kmp_all(b), kmp_all(c)
        ans = inf
        la, lb, lc = len(a), len(b), len(c)
        for start in pos_a:
            ib = bisect_left(pos_b, start + la)
            if ib == len(pos_b):
                continue
            ic = bisect_left(pos_c, pos_b[ib] + lb)
            if ic < len(pos_c):
                ans = min(ans, pos_c[ic] + lc - start)
        return -1 if ans == inf else int(ans)
# @lc code=end
