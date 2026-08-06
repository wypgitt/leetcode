#
# @lc app=leetcode id=3714 lang=python3
#
# [3714] Longest Balanced Substring II
#
# https://leetcode.com/problems/longest-balanced-substring-ii/description/
#
# algorithms
# Medium (41.90%)
# Likes:    582
# Dislikes: 137
# Total Accepted:    76.4K
# Total Submissions: 182.3K
# Testcase Example:  "\"abbac\""
#
#
# You are given a string s consisting only of the characters 'a', 'b', and
# 'c'.
#
# A substring of s is called balanced if all distinct characters in the
# substring appear the same number of times.
#
# Return the length of the longest balanced substring of s.
#
# Example 1:
#
# Input: s = "abbac"
#
# Output: 4
#
# Explanation:
#
# The longest balanced substring is "abba" because both distinct
# characters 'a' and 'b' each appear exactly 2 times.
#
# Example 2:
#
# Input: s = "aabcc"
#
# Output: 3
#
# Explanation:
#
# The longest balanced substring is "abc" because all distinct characters
# 'a', 'b' and 'c' each appear exactly 1 time.
#
# Example 3:
#
# Input: s = "aba"
#
# Output: 2
#
# Explanation:
#
# One of the longest balanced substrings is "ab" because both distinct
# characters 'a' and 'b' each appear exactly 1 time. Another longest
# balanced substring is "ba".
#
# Constraints:
#
# 1 <= s.length <= 10^5
#
# s contains only the characters 'a', 'b', and 'c'.
#

# @lc code=start

from collections import Counter


class Solution:
    def longestBalanced(self, s: str) -> int:
        """
        Interview explanation:
        With alphabet {a,b,c}, the longest balanced substring is the max of:
        one-char runs, equal-count two-char segments, or equal a/b/c counts.

        Algorithm:
        - calc1: longest run of a single character.
        - calc2(a,b): on segments using only a/b, prefix (+1/-1) + first-seen map.
        - calc3: map (cnt_a-cnt_b, cnt_b-cnt_c) first index for equal triple counts.
        - Return max over calc1, three calc2 pairs, and calc3.

        Complexity: O(n) time, O(n) space.
        """
        def calc1(s: str) -> int:
            res = i = 0
            n = len(s)
            while i < n:
                j = i + 1
                while j < n and s[j] == s[i]:
                    j += 1
                res = max(res, j - i)
                i = j
            return res

        def calc2(s: str, a: str, b: str) -> int:
            res = i = 0
            n = len(s)
            while i < n:
                while i < n and s[i] not in (a, b):
                    i += 1
                pos = {0: i - 1}
                d = 0
                while i < n and s[i] in (a, b):
                    d += 1 if s[i] == a else -1
                    if d in pos:
                        res = max(res, i - pos[d])
                    else:
                        pos[d] = i
                    i += 1
            return res

        def calc3(s: str) -> int:
            pos = {(0, 0): -1}
            cnt = Counter()
            res = 0
            for i, c in enumerate(s):
                cnt[c] += 1
                k = (cnt["a"] - cnt["b"], cnt["b"] - cnt["c"])
                if k in pos:
                    res = max(res, i - pos[k])
                else:
                    pos[k] = i
            return res

        x = calc1(s)
        y = max(calc2(s, "a", "b"), calc2(s, "b", "c"), calc2(s, "a", "c"))
        return max(x, y, calc3(s))
# @lc code=end
