#
# @lc app=leetcode id=1639 lang=python3
#
# [1639] Number of Ways to Form a Target String Given a Dictionary
#
# https://leetcode.com/problems/number-of-ways-to-form-a-target-string-given-a-dictionary/description/
#
# algorithms
# Hard (56.35%)
# Likes:    2082
# Dislikes: 120
# Total Accepted:    136K
# Total Submissions: 241K
# Testcase Example:  "[\"acca\",\"bbbb\",\"caca\"]"
#
# You are given a list of strings of the same length words and a string target.
#
# Your task is to form target using the given words under the following rules:
#
# target should be formed from left to right.
#
# To form the i^th character (0-indexed) of target, you can choose the k^th
# character of the j^th string in words if target[i] = words[j][k].
#
# Once you use the k^th character of the j^th string of words, you can no
# longer use the x^th character of any string in words where x <= k. In other
# words, all characters to the left of or at index k become unusuable for every
# string.
#
# Repeat the process until you form the string target.
#
# Notice that you can use multiple characters from the same string in words
# provided the conditions above are met.
#
# Return the number of ways to form target from words. Since the answer may be
# too large, return it modulo 10^9 + 7.
#
# Example 1:
#
# Input: words = ["acca","bbbb","caca"], target = "aba"
# Output: 6
# Explanation: There are 6 ways to form target.
# "aba" -> index 0 ("acca"), index 1 ("bbbb"), index 3 ("caca")
# "aba" -> index 0 ("acca"), index 2 ("bbbb"), index 3 ("caca")
# "aba" -> index 0 ("acca"), index 1 ("bbbb"), index 3 ("acca")
# "aba" -> index 0 ("acca"), index 2 ("bbbb"), index 3 ("acca")
# "aba" -> index 1 ("caca"), index 2 ("bbbb"), index 3 ("acca")
# "aba" -> index 1 ("caca"), index 2 ("bbbb"), index 3 ("caca")
#
# Example 2:
#
# Input: words = ["abba","baab"], target = "bab"
# Output: 4
# Explanation: There are 4 ways to form target.
# "bab" -> index 0 ("baab"), index 1 ("baab"), index 2 ("abba")
# "bab" -> index 0 ("baab"), index 1 ("baab"), index 3 ("baab")
# "bab" -> index 0 ("baab"), index 2 ("baab"), index 3 ("baab")
# "bab" -> index 1 ("abba"), index 2 ("baab"), index 3 ("baab")
#
# Constraints:
#
# 1 <= words.length <= 1000
#
# 1 <= words[i].length <= 1000
#
# All strings in words have the same length.
#
# 1 <= target.length <= 1000
#
# words[i] and target contain only lowercase English letters.
#

# @lc code=start
from typing import List
from functools import lru_cache
from collections import Counter


class Solution:
    def numWays(self, words: List[str], target: str) -> int:
        """
        Interview explanation:
        Form target by picking letters left-to-right from dictionary words,
        using at most one char per column (same index across words). DP on
        (target index, column).

        Algorithm (bottom-up DP):
        - cnt[col][char] = how many words have that char at col.
        - dp[j] = ways to form target[:j]; iterate columns updating backward.

        Complexity: O(C * (W + T)) with C=word length, T=|target|.
        """
        MOD = 10**9 + 7
        m = len(words[0])
        t = len(target)
        cnt = [Counter() for _ in range(m)]
        for w in words:
            for i, ch in enumerate(w):
                cnt[i][ch] += 1
        dp = [0] * (t + 1)
        dp[0] = 1
        for col in range(m):
            for j in range(t, 0, -1):
                dp[j] = (dp[j] + dp[j - 1] * cnt[col][target[j - 1]]) % MOD
        return dp[t]

    def numWays_memo(self, words: List[str], target: str) -> int:
        """
        Interview explanation:
        Alternate top-down memo: dfs(ti, col) ways to form target[ti:] from columns
        >= col.

        Algorithm (DFS + memo):
        - Skip column or use column if letter matches (multiply by count).

        Complexity: O(C*T) states, O(C*T) time.
        """
        MOD = 10**9 + 7
        m = len(words[0])
        tlen = len(target)
        cnt = [Counter() for _ in range(m)]
        for w in words:
            for i, ch in enumerate(w):
                cnt[i][ch] += 1

        @lru_cache(None)
        def dfs(ti: int, col: int) -> int:
            if ti == tlen:
                return 1
            if col == m:
                return 0
            # skip
            ans = dfs(ti, col + 1)
            # use
            ans = (ans + cnt[col][target[ti]] * dfs(ti + 1, col + 1)) % MOD
            return ans

        return dfs(0, 0)
# @lc code=end
