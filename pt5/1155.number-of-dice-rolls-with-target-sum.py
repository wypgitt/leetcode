from __future__ import annotations


class Solution:
    def numRollsToTarget(self, n: int, k: int, target: int) -> int:
        mod = 10**9 + 7
        dp = [0] * (target + 1)
        dp[0] = 1

        for _ in range(n):
            next_dp = [0] * (target + 1)
            for total in range(1, target + 1):
                ways = 0
                for face in range(1, min(k, total) + 1):
                    ways += dp[total - face]
                next_dp[total] = ways % mod
            dp = next_dp

        return dp[target]

