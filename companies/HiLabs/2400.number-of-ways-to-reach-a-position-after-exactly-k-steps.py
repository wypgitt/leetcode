#
# @lc app=leetcode id=2400 lang=python3
#
# [2400] Number of Ways to Reach a Position After Exactly k Steps
#
# https://leetcode.com/problems/number-of-ways-to-reach-a-position-after-exactly-k-steps/description/
#
# algorithms
# Medium (37.20%)
# Likes:    852
# Dislikes: 68
# Total Accepted:    40.9K
# Total Submissions: 109.9K
# Testcase Example:  "1\n2\n3"
#
# You are given two positive integers startPos and endPos. Initially, you are
# standing at position startPos on an infinite number line. With one step, you
# can move either one position to the left, or one position to the right.
#
# Given a positive integer k, return the number of different ways to reach the
# position endPos starting from startPos, such that you perform exactly k steps.
# Since the answer may be very large, return it modulo 10^9 + 7.
#
# Two ways are considered different if the order of the steps made is not
# exactly the same.
#
# Note that the number line includes negative integers.
#
#
#
# Example 1:
#
# Input: startPos = 1, endPos = 2, k = 3
# Output: 3
# Explanation: We can reach position 2 from 1 in exactly 3 steps in three ways:
# - 1 -> 2 -> 3 -> 2.
# - 1 -> 2 -> 1 -> 2.
# - 1 -> 0 -> 1 -> 2.
# It can be proven that no other way is possible, so we return 3.
#
# Example 2:
#
# Input: startPos = 2, endPos = 5, k = 10
# Output: 0
# Explanation: It is impossible to reach position 5 from position 2 in exactly
# 10 steps.
#
#
#
# Constraints:
#
#
# 1 <= startPos, endPos, k <= 1000
#

# @lc code=start

from math import comb


class Solution:
    def numberOfWays(self, startPos: int, endPos: int, k: int) -> int:
        """
        Interview explanation:
        From startPos, each step +1 or -1. Ways to reach endPos in exactly k
        steps mod 10^9+7.

        Algorithm:
        - Need d = |end-start| <= k and (k-d) even. Right steps = (k+d)/2;
          answer C(k, right).

        Complexity: O(k) time for comb, O(1) space.
        """
        MOD = 10**9 + 7
        d = abs(endPos - startPos)
        if d > k or (k - d) % 2:
            return 0
        right = (k + d) // 2
        return comb(k, right) % MOD

    def numberOfWays_dp(self, startPos: int, endPos: int, k: int) -> int:
        """
        Interview explanation:
        Alternate: DP on steps and offset position (or relative distance).

        Algorithm:
        - dp[steps][pos_offset]; or 1D rolling over reachable offsets.

        Complexity: O(k^2) time, O(k) space.
        """
        MOD = 10**9 + 7
        d = abs(endPos - startPos)
        if d > k or (k - d) % 2:
            return 0
        # dp[i] = ways to be at offset i after some steps; offset shift by k
        # relative: start at 0, end at endPos-startPos
        target = endPos - startPos
        # positions from -k..k -> index + k
        dp = [0] * (2 * k + 1)
        dp[k] = 1
        for _ in range(k):
            ndp = [0] * (2 * k + 1)
            for i in range(2 * k + 1):
                if dp[i]:
                    if i + 1 <= 2 * k:
                        ndp[i + 1] = (ndp[i + 1] + dp[i]) % MOD
                    if i - 1 >= 0:
                        ndp[i - 1] = (ndp[i - 1] + dp[i]) % MOD
            dp = ndp
        return dp[k + target]
# @lc code=end
