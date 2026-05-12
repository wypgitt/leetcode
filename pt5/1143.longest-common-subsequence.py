from __future__ import annotations


class Solution:
    def longestCommonSubsequence(self, text1: str, text2: str) -> int:
        if len(text2) > len(text1):
            text1, text2 = text2, text1

        dp = [0] * (len(text2) + 1)
        for char1 in text1:
            previous_diagonal = 0
            for j, char2 in enumerate(text2, start=1):
                saved = dp[j]
                if char1 == char2:
                    dp[j] = previous_diagonal + 1
                else:
                    dp[j] = max(dp[j], dp[j - 1])
                previous_diagonal = saved

        return dp[-1]

