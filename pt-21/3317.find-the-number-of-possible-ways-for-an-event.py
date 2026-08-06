#
# @lc app=leetcode id=3317 lang=python3
#
# [3317] Find the Number of Possible Ways for an Event
#
# https://leetcode.com/problems/find-the-number-of-possible-ways-for-an-event/description/
#
# algorithms
# Hard (34.29%)
# Likes:    78
# Dislikes: 15
# Total Accepted:    5.5K
# Total Submissions: 16.2K
# Testcase Example:  "1\n2\n3"
#
#
# You are given three integers n, x, and y.
#
# An event is being held for n performers. When a performer arrives, they
# are assigned to one of the x stages. All performers assigned to the same
# stage will perform together as a band, though some stages might remain
# empty.
#
# After all performances are completed, the jury will award each band a
# score in the range [1, y].
#
# Return the total number of possible ways the event can take place.
#
# Since the answer may be very large, return it modulo 10^9 + 7.
#
# Note that two events are considered to have been held differently if
# either of the following conditions is satisfied:
#
# Any performer is assigned a different stage.
#
# Any band is awarded a different score.
#
# Example 1:
#
# Input: n = 1, x = 2, y = 3
#
# Output: 6
#
# Explanation:
#
# There are 2 ways to assign a stage to the performer.
#
# The jury can award a score of either 1, 2, or 3 to the only band.
#
# Example 2:
#
# Input: n = 5, x = 2, y = 1
#
# Output: 32
#
# Explanation:
#
# Each performer will be assigned either stage 1 or stage 2.
#
# All bands will be awarded a score of 1.
#
# Example 3:
#
# Input: n = 3, x = 3, y = 4
#
# Output: 684
#
# Constraints:
#
# 1 <= n, x, y <= 1000
#

# @lc code=start
class Solution:
    def numberOfWays(self, n: int, x: int, y: int) -> int:
        """
        Interview explanation:
        Assign n labeled performers to x labeled stages (empty OK), then score
        each non-empty band in [1, y]. Count configurations mod 1e9+7.

        Algorithm:
        - For k non-empty stages: S(n,k) * P(x,k) * y^k.
        - DP Stirling 2nd kind: S[i][j] = S[i-1][j-1] + j*S[i-1][j].
        - Accumulate over k = 1..min(n,x).

        Complexity: O(n * min(n,x)) time, O(n * min(n,x)) space.
        """
        MOD = 10**9 + 7
        m = min(n, x)
        S = [[0] * (m + 1) for _ in range(n + 1)]
        S[0][0] = 1
        for i in range(1, n + 1):
            for j in range(1, min(i, m) + 1):
                S[i][j] = (S[i - 1][j - 1] + j * S[i - 1][j]) % MOD

        ans = 0
        perm = 1
        yk = 1
        for k in range(1, m + 1):
            perm = perm * (x - k + 1) % MOD
            yk = yk * y % MOD
            ans = (ans + S[n][k] * perm % MOD * yk) % MOD
        return ans
# @lc code=end
