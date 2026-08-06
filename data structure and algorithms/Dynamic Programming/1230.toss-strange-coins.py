#
# @lc app=leetcode id=1230 lang=python3
#
# [1230] Toss Strange Coins
#
# https://leetcode.com/problems/toss-strange-coins/description/
#
# algorithms
# Medium (58.08%)
# Likes:    410
# Dislikes: 53
# Total Accepted:    23.4K
# Total Submissions: 40.2K
# Testcase Example:  "[0.4]\n1"
#
#
# You have some coins.  The i-th coin has a probability prob[i] of facing
# heads when tossed.
#
# Return the probability that the number of coins facing heads equals
# target if you toss every coin exactly once.
#
# Example 1:
#
# Input: prob = [0.4], target = 1
# Output: 0.40000
#
# Example 2:
#
# Input: prob = [0.5,0.5,0.5,0.5,0.5], target = 0
# Output: 0.03125
#
# Constraints:
#
# 1 <= prob.length <= 1000
#
# 0 <= prob[i] <= 1
#
# 0 <= target <= prob.length
#
# Answers will be accepted as correct if they are within 10^-5 of the
# correct answer.
#
# @lc code=start
from typing import List

class Solution:
    def probabilityOfHeads(self, prob: List[float], target: int) -> float:
        """
        Interview explanation:
        Premium. Each coin i lands heads with prob[i] independently. Probability
        of exactly `target` heads. DP: dp[j] = prob of j heads so far.

        Algorithm:
        - dp[0]=1; for each p: update dp backward dp[j]=dp[j]*(1-p)+dp[j-1]*p

        Complexity: O(n * target) time, O(target) space.
        """
        dp = [0.0] * (target + 1)
        dp[0] = 1.0
        for p in prob:
            for j in range(target, -1, -1):
                dp[j] = dp[j] * (1 - p) + (dp[j - 1] * p if j > 0 else 0.0)
        return dp[target]
# @lc code=end
