#
# @lc app=leetcode id=1269 lang=python3
#
# [1269] Number of Ways to Stay in the Same Place After Some Steps
#
# https://leetcode.com/problems/number-of-ways-to-stay-in-the-same-place-after-some-steps/description/
#
# algorithms
# Hard (50.16%)
# Likes:    1611
# Dislikes: 67
# Total Accepted:    106K
# Total Submissions: 211K
# Testcase Example:  "3"
#
# You have a pointer at index 0 in an array of size arrLen. At each step, you
# can move 1 position to the left, 1 position to the right in the array, or
# stay in the same place (The pointer should not be placed outside the array at
# any time).
#
# Given two integers steps and arrLen, return the number of ways such that your
# pointer is still at index 0 after exactly steps steps. Since the answer may
# be too large, return it modulo 10^9 + 7.
#
# Example 1:
#
# Input: steps = 3, arrLen = 2
# Output: 4
# Explanation: There are 4 differents ways to stay at index 0 after 3 steps.
# Right, Left, Stay
# Stay, Right, Left
# Right, Stay, Left
# Stay, Stay, Stay
#
# Example 2:
#
# Input: steps = 2, arrLen = 4
# Output: 2
# Explanation: There are 2 differents ways to stay at index 0 after 2 steps
# Right, Left
# Stay, Stay
#
# Example 3:
#
# Input: steps = 4, arrLen = 2
# Output: 8
#
# Constraints:
#
# 1 <= steps <= 500
#
# 1 <= arrLen <= 10^6
#

# @lc code=start

class Solution:
    def numWays(self, steps: int, arrLen: int) -> int:
        """
        Interview explanation:
        Ways to return to index 0 after exactly `steps` moves on [0..arrLen-1].
        DP: dp[i]=ways to be at i; can only reach indices <= steps and < arrLen.
        Bound width = min(arrLen, steps//2+1).

        Algorithm:
        - MOD; maxPos=min(arrLen-1, steps).
        - dp[0]=1; for each step update from left/stay/right neighbors.
        - Return dp[0].

        Complexity: O(steps * min(arrLen, steps)) time/space.
        """
        MOD = 10**9 + 7
        max_pos = min(arrLen - 1, steps)
        dp = [0] * (max_pos + 1)
        dp[0] = 1
        for _ in range(steps):
            ndp = [0] * (max_pos + 1)
            for i in range(max_pos + 1):
                ndp[i] = dp[i]
                if i > 0:
                    ndp[i] = (ndp[i] + dp[i - 1]) % MOD
                if i < max_pos:
                    ndp[i] = (ndp[i] + dp[i + 1]) % MOD
            dp = ndp
        return dp[0]
# @lc code=end
