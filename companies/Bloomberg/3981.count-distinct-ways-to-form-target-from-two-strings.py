#
# @lc app=leetcode id=3981 lang=python3
#
# [3981] Count Distinct Ways to Form Target from Two Strings
#
# https://leetcode.com/problems/count-distinct-ways-to-form-target-from-two-strings/description/
#
# algorithms
# Hard (46.55%)
# Likes:    48
# Dislikes: 3
# Total Accepted:    7.8K
# Total Submissions: 16.8K
# Testcase Example:  "\"abc\"\n\"bac\"\n\"abc\""
#
#
# You are given three strings word1, word2, and target.
#
# Your task is to count the number of ways to form target by choosing
# characters from word1 and word2 under the following conditions:
#
# For each character of target, choose one matching character from either
# word1 or word2.
#
# The chosen indices from word1 must be strictly increasing.
#
# The chosen indices from word2 must be strictly increasing.
#
# At least one character must be chosen from both word1 and word2.
#
# Two ways are considered different if, for at least one position in
# target, the chosen character comes from a different string or a
# different index.
#
# Return the number of ways. Since the answer may be very large, return it
# modulo 10^9 + 7.
#
# Example 1:
#
# Input: word1 = "abc", word2 = "bac", target = "abc"
#
# Output: 5
#
# Explanation:
#
# There are 5 ways to form target:
#
# word1[0] = 'a', word1[1] = 'b', word2[2] = 'c'
#
# word1[0] = 'a', word2[0] = 'b', word1[2] = 'c'
#
# word1[0] = 'a', word2[0] = 'b', word2[2] = 'c'
#
# word2[1] = 'a', word1[1] = 'b', word1[2] = 'c'
#
# word2[1] = 'a', word1[1] = 'b', word2[2] = 'c'
#
# All ways preserve the increasing index order inside each string and
# choose at least one character from each string.
#
# Example 2:
#
# Input: word1 = "cd", word2 = "cd", target = "ccd"
#
# Output: 4
#
# Explanation:
#
# There are 4 ways to form target:
#
# word1[0] = 'c', word2[0] = 'c', word1[1] = 'd'
#
# word1[0] = 'c', word2[0] = 'c', word2[1] = 'd'
#
# word2[0] = 'c', word1[0] = 'c', word1[1] = 'd'
#
# word2[0] = 'c', word1[0] = 'c', word2[1] = 'd'
#
# The first two 'c' characters in target must come one from each string.
# The final 'd' can be chosen from either string.
#
# Example 3:
#
# Input: word1 = "xy", word2 = "xy", target = "xyxy"
#
# Output: 2
#
# Explanation:
#
# There are 2 ways to form target:
#
# word1[0] = 'x', word1[1] = 'y', word2[0] = 'x', word2[1] = 'y'
#
# word2[0] = 'x', word2[1] = 'y', word1[0] = 'x', word1[1] = 'y'
#
# Each "xy" part in target comes entirely from one string.
#
# Example 4:
#
# Input: word1 = "ab", word2 = "cde", target = "ace"
#
# Output: 1
#
# Explanation:
#
# The only way is to choose word1[0] = 'a', word2[0] = 'c', and word2[2] =
# 'e'. Thus, the answer is 1.
#
# Constraints:
#
# 1 <= word1.length, word2.length, target.length <= 100
#
# word1, word2, and target consist of lowercase English letters only.
#

# @lc code=start

from functools import cache


class Solution:
    def interleaveCharacters(self, word1: str, word2: str, target: str) -> int:
        """
        Interview explanation:
        Form target by walking increasing indices in each word; mask tracks that
        both words contribute at least once.

        Algorithm:
        - DFS(t, i, j, mask): place target[t] from word1[i:] or word2[j:].
        - Memoize; at t == len(target) accept only mask == 3.
        - Return ways modulo 10^9+7.

        Complexity: O(|t|*|w1|*|w2|*(|w1|+|w2|)) time, O(|t|*|w1|*|w2|) space.
        """
        MOD = 10**9 + 7
        n1, n2, nt = len(word1), len(word2), len(target)

        @cache
        def dfs(t: int, i: int, j: int, mask: int) -> int:
            if t == nt:
                return 1 if mask == 3 else 0
            res = 0
            ch = target[t]
            for ni in range(i, n1):
                if word1[ni] == ch:
                    res += dfs(t + 1, ni + 1, j, mask | 1)
            for nj in range(j, n2):
                if word2[nj] == ch:
                    res += dfs(t + 1, i, nj + 1, mask | 2)
            return res % MOD

        return dfs(0, 0, 0, 0)
# @lc code=end
