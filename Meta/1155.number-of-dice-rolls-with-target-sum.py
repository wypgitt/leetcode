#
# @lc app=leetcode id=1155 lang=python3
#
# [1155] Number of Dice Rolls With Target Sum
#
# https://leetcode.com/problems/number-of-dice-rolls-with-target-sum/description/
#
# algorithms
# Medium (62.52%)
# Likes:    5355
# Dislikes: 188
# Total Accepted:    360K
# Total Submissions: 576K
# Testcase Example:  "1"
#
# You have n dice, and each dice has k faces numbered from 1 to k.
#
# Given three integers n, k, and target, return the number of possible ways
# (out of the k^n total ways) to roll the dice, so the sum of the face-up
# numbers equals target. Since the answer may be too large, return it modulo
# 10^9 + 7.
#
# Example 1:
#
# Input: n = 1, k = 6, target = 3
# Output: 1
# Explanation: You throw one die with 6 faces.
# There is only one way to get a sum of 3.
#
# Example 2:
#
# Input: n = 2, k = 6, target = 7
# Output: 6
# Explanation: You throw two dice, each with 6 faces.
# There are 6 ways to get a sum of 7: 1+6, 2+5, 3+4, 4+3, 5+2, 6+1.
#
# Example 3:
#
# Input: n = 30, k = 30, target = 500
# Output: 222616187
# Explanation: The answer must be returned modulo 10^9 + 7.
#
# Constraints:
#
# 1 <= n, k <= 30
#
# 1 <= target <= 1000
#

# @lc code=start
class Solution:
    def numRollsToTarget(self, n: int, k: int, target: int) -> int:
        """
        Interview explanation:
        Ways to roll n dice with faces 1..k summing to target. Classic DP:
        dp[dice][sum].

        Algorithm (DP):
        - dp[0]=1; for each die, update ways for sums using faces 1..k.
        - Use rolling array backwards or two arrays; mod 10^9+7.

        Complexity: O(n * target * k) time, O(target) space.
        """
        MOD = 10**9 + 7
        dp = [0] * (target + 1)
        dp[0] = 1
        for _ in range(n):
            ndp = [0] * (target + 1)
            for s in range(target + 1):
                if dp[s] == 0:
                    continue
                for face in range(1, k + 1):
                    if s + face <= target:
                        ndp[s + face] = (ndp[s + face] + dp[s]) % MOD
            dp = ndp
        return dp[target]
# @lc code=end
