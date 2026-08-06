#
# @lc app=leetcode id=1621 lang=python3
#
# [1621] Number of Sets of K Non-Overlapping Line Segments
#
# https://leetcode.com/problems/number-of-sets-of-k-non-overlapping-line-segments/description/
#
# algorithms
# Medium (46.19%)
# Likes:    494
# Dislikes: 50
# Total Accepted:    13.9K
# Total Submissions: 30.1K
# Testcase Example:  "4"
#
# Given n points on a 1-D plane, where the i^th point (from 0 to n-1) is at x =
# i, find the number of ways we can draw exactly k non-overlapping line
# segments such that each segment covers two or more points. The endpoints of
# each segment must have integral coordinates. The k line segments do not have
# to cover all n points, and they are allowed to share endpoints.
#
# Return the number of ways we can draw k non-overlapping line segments. Since
# this number can be huge, return it modulo 10^9 + 7.
#
# Example 1:
#
# Input: n = 4, k = 2
# Output: 5
# Explanation: The two line segments are shown in red and blue.
# The image above shows the 5 different ways {(0,2),(2,3)}, {(0,1),(1,3)},
# {(0,1),(2,3)}, {(1,2),(2,3)}, {(0,1),(1,2)}.
#
# Example 2:
#
# Input: n = 3, k = 1
# Output: 3
# Explanation: The 3 ways are {(0,1)}, {(0,2)}, {(1,2)}.
#
# Example 3:
#
# Input: n = 30, k = 7
# Output: 796297179
# Explanation: The total number of possible ways to draw 7 line segments is
# 3796297200. Taking this number modulo 10^9 + 7 gives us 796297179.
#
# Constraints:
#
# 2 <= n <= 1000
#
# 1 <= k <= n-1
#

# @lc code=start
class Solution:
    def numberOfSets(self, n: int, k: int) -> int:
        """
        Interview explanation:
        Count ways to draw k non-overlapping line segments on n points on a line
        (endpoints from 1..n). Combinatorial: C(n+k-1, 2k) or DP.

        Algorithm (combinatorics):
        - Answer = C(n + k - 1, 2*k) mod 1e9+7 (known closed form via stars/bars
          / mapping to choosing 2k endpoints with reuse of touching points).

        Complexity: O(n+k) time for factorial, O(n+k) space.
        """
        MOD = 10**9 + 7
        # C(n+k-1, 2k)
        N = n + k - 1
        R = 2 * k
        if R > N:
            return 0
        fac = [1] * (N + 1)
        for i in range(1, N + 1):
            fac[i] = fac[i - 1] * i % MOD
        invfac = [1] * (N + 1)
        invfac[N] = pow(fac[N], MOD - 2, MOD)
        for i in range(N, 0, -1):
            invfac[i - 1] = invfac[i] * i % MOD
        return fac[N] * invfac[R] % MOD * invfac[N - R] % MOD

    def numberOfSets_dp(self, n: int, k: int) -> int:
        """
        Interview explanation:
        Alternate DP: dp[i][j] = ways using first i points and j segments.
        Transitions: skip point i, or end a segment at i.

        Algorithm (DP):
        - dp[i][j] with prefix sums optimization; O(n*k) after opt, O(n^2 k) naive.

        Complexity: O(n*k) time with prefix, O(n*k) space.
        """
        MOD = 10**9 + 7
        # dp[points_used][segments] — use 1-index points 1..n
        dp = [[0] * (k + 1) for _ in range(n + 1)]
        dp[0][0] = 1
        # Simpler recurrence via combinatorics-backed DP:
        # numberOfSets(n,k) = numberOfSets(n-1,k) + sum numberOfSets(i,k-1) for segments ending at n
        # Optimized: dp[i][j] ways for i points j segments
        dp = [[0] * (k + 1) for _ in range(n + 1)]
        for i in range(n + 1):
            dp[i][0] = 1
        for j in range(1, k + 1):
            pref = 0
            # use running sum of dp[t][j-1] for t
            # standard: dp[i][j] = dp[i-1][j] + sum_{t=0}^{i-2} dp[t][j-1]
            # = dp[i-1][j] + pref where pref accumulates
            sum_prev = 0
            for i in range(1, n + 1):
                dp[i][j] = (dp[i - 1][j] + sum_prev) % MOD
                # after considering point i as available end, add dp[i-1][j-1] for next
                if i >= 1:
                    sum_prev = (sum_prev + dp[i - 1][j - 1]) % MOD
        return dp[n][k]
# @lc code=end
