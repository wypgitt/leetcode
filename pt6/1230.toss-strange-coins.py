#
# @lc app=leetcode id=1230 lang=python3
#
# [1230] Toss Strange Coins
#
# https://leetcode.com/problems/toss-strange-coins/description/
#
# algorithms
# Medium (58.09%)
# Likes:    410
# Dislikes: 53
# Total Accepted:    23.2K
# Total Submissions: 40K
# Testcase Example:  '[0.4]\n1'
#
# You have some coins.  The i-th coin has a probability prob[i] of facing heads
# when tossed.
# 
# Return the probability that the number of coins facing heads equals target if
# you toss every coin exactly once.
# 
# 
# Example 1:
# Input: prob = [0.4], target = 1
# Output: 0.40000
# Example 2:
# Input: prob = [0.5,0.5,0.5,0.5,0.5], target = 0
# Output: 0.03125
# 
# 
# Constraints:
# 
# 
# 1 <= prob.length <= 1000
# 0 <= prob[i] <= 1
# 0 <= target <= prob.length
# Answers will be accepted as correct if they are within 10^-5 of the correct
# answer.
# 
# 
#

# @lc code=start
from typing import List


class Solution:
    def probabilityOfHeads(self, prob: List[float], target: int) -> float:
        dp = [0.0] * (target + 1)
        dp[0] = 1.0

        for p in prob:
            for heads in range(target, 0, -1):
                dp[heads] = dp[heads] * (1 - p) + dp[heads - 1] * p
            dp[0] *= 1 - p

        return dp[target]
# @lc code=end

# Explanation
# -----------
# dp[h] means the probability of seeing exactly h heads after processing the
# coins so far. For a coin with probability p, the new probability for h heads
# is: previous h heads and this coin tails, plus previous h - 1 heads and this
# coin heads.
#
# We update heads counts from target down to 1 so dp[h - 1] still refers to the
# previous coin layer. This is the standard 0/1-DP compression pattern.
#
# Edge cases: target = 0 only keeps multiplying tail probabilities; target
# larger than processed coins naturally stays at 0; probabilities 0 and 1 work
# without special cases.
#
# Time complexity: O(n * target).
# Space complexity: O(target).
