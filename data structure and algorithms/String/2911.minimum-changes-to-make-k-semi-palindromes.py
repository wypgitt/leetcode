#
# @lc app=leetcode id=2911 lang=python3
#
# [2911] Minimum Changes to Make K Semi-palindromes
#
# https://leetcode.com/problems/minimum-changes-to-make-k-semi-palindromes/description/
#
# algorithms
# Hard (35.01%)
# Likes:    132
# Dislikes: 108
# Total Accepted:    5.5K
# Total Submissions: 15.7K
# Testcase Example:  "\"abcac\"\n2"
#
#
# Given a string s and an integer k, partition s into k substrings such
# that the letter changes needed to make each substring a semi-palindrome
# are minimized.
#
# Return the minimum number of letter changes required.
#
# A semi-palindrome is a special type of string that can be divided into
# palindromes based on a repeating pattern. To check if a string is a
# semi-palindrome:​
#
# Choose a positive divisor d of the string's length. d can range from 1
# up to, but not including, the string's length. For a string of length 1,
# it does not have a valid divisor as per this definition, since the only
# divisor is its length, which is not allowed.
#
# For a given divisor d, divide the string into groups where each group
# contains characters from the string that follow a repeating pattern of
# length d. Specifically, the first group consists of characters at
# positions 1, 1 + d, 1 + 2d, and so on; the second group includes
# characters at positions 2, 2 + d, 2 + 2d, etc.
#
# The string is considered a semi-palindrome if each of these groups forms
# a palindrome.
#
# Consider the string "abcabc":
#
# The length of "abcabc" is 6. Valid divisors are 1, 2, and 3.
#
# For d = 1: The entire string "abcabc" forms one group. Not a palindrome.
#
# For d = 2:
#
# Group 1 (positions 1, 3, 5): "acb"
#
# Group 2 (positions 2, 4, 6): "bac"
#
# Neither group forms a palindrome.
#
# For d = 3:
#
# Group 1 (positions 1, 4): "aa"
#
# Group 2 (positions 2, 5): "bb"
#
# Group 3 (positions 3, 6): "cc"
#
# All groups form palindromes. Therefore, "abcabc" is a semi-palindrome.
#
# Example 1:
#
# Input:   s = "abcac", k = 2
#
# Output:   1
#
# Explanation:  Divide s into "ab" and "cac". "cac" is already
# semi-palindrome. Change "ab" to "aa", it becomes semi-palindrome with d
# = 1.
#
# Example 2:
#
# Input:   s = "abcdef", k = 2
#
# Output:   2
#
# Explanation:  Divide s into substrings "abc" and "def". Each needs one
# change to become semi-palindrome.
#
# Example 3:
#
# Input:   s = "aabbaa", k = 3
#
# Output:   0
#
# Explanation:  Divide s into substrings "aa", "bb" and "aa". All are
# already semi-palindromes.
#
# Constraints:
#
# 2 <= s.length <= 200
#
# 1 <= k <= s.length / 2
#
# s contains only lowercase English letters.
#

# @lc code=start
from functools import lru_cache
from math import inf


class Solution:
    def minimumChanges(self, s: str, k: int) -> int:
        """
        Interview explanation:
        Partition s into k substrings; minimize total letter changes so each
        piece is a semi-palindrome (some d | len, d < len, each residue class
        mod d is a palindrome). Length-1 strings are never semi-palindromes.

        Algorithm:
        - Precompute cost[i][j] = min changes for s[i..j] over valid d.
        - DP: dp[i][p] = min cost to cover s[:i] with p pieces.

        Complexity: O(n^3 + n^2 * k) time roughly, O(n^2) space.
        """
        n = len(s)

        def changes_for_d(i: int, j: int, d: int) -> int:
            # groups: for offset o in 0..d-1, chars s[i+o], s[i+o+d], ...
            length = j - i + 1
            chg = 0
            for o in range(d):
                # collect indices in this group
                idxs = list(range(i + o, j + 1, d))
                L, R = 0, len(idxs) - 1
                while L < R:
                    if s[idxs[L]] != s[idxs[R]]:
                        chg += 1
                    L += 1
                    R -= 1
            return chg

        cost = [[inf] * n for _ in range(n)]
        for i in range(n):
            for j in range(i + 1, n):  # length >= 2
                length = j - i + 1
                best = inf
                for d in range(1, length):
                    if length % d == 0:
                        best = min(best, changes_for_d(i, j, d))
                cost[i][j] = best

        @lru_cache(None)
        def dp(i: int, parts: int) -> int:
            if parts == 0:
                return 0 if i == n else inf
            if i >= n:
                return inf
            best = inf
            # need remaining parts-1 pieces after this one; each length >= 2
            for j in range(i + 1, n - 2 * (parts - 1)):
                if cost[i][j] < inf:
                    best = min(best, cost[i][j] + dp(j + 1, parts - 1))
            return best

        return int(dp(0, k))
# @lc code=end
