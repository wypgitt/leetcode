#
# @lc app=leetcode id=837 lang=python3
#
# [837] New 21 Game
#
# https://leetcode.com/problems/new-21-game/description/
#
# algorithms
# Medium (51.94%)
# Likes:    2514
# Dislikes: 2011
# Total Accepted:    163K
# Total Submissions: 314K
# Testcase Example:  "10"
#
# Alice plays the following game, loosely based on the card game "21".
#
# Alice starts with 0 points and draws numbers while she has less than k
# points. During each draw, she gains an integer number of points randomly from
# the range [1, maxPts], where maxPts is an integer. Each draw is independent
# and the outcomes have equal probabilities.
#
# Alice stops drawing numbers when she gets k or more points.
#
# Return the probability that Alice has n or fewer points.
#
# Answers within 10^-5 of the actual answer are considered accepted.
#
# Example 1:
#
# Input: n = 10, k = 1, maxPts = 10
# Output: 1.00000
# Explanation: Alice gets a single card, then stops.
#
# Example 2:
#
# Input: n = 6, k = 1, maxPts = 10
# Output: 0.60000
# Explanation: Alice gets a single card, then stops.
# In 6 out of 10 possibilities, she is at or below 6 points.
#
# Example 3:
#
# Input: n = 21, k = 17, maxPts = 10
# Output: 0.73278
#
# Constraints:
#
# 0 <= k <= n <= 10^4
#
# 1 <= maxPts <= 10^4
#

# @lc code=start

class Solution:
    def new21Game(self, n: int, k: int, maxPts: int) -> float:
        """
        Interview explanation:
        Alice draws 1..maxPts uniformly while score < k, then stops. Probability
        final score ≤ n. dp[i] = Prob of reaching i; sliding window of last
        maxPts probabilities for scores still drawing (<k).

        Algorithm (DP + sliding window):
        - If k==0 or n≥k-1+maxPts: return 1.
        - dp[0]=1; window=1; for i=1..n: dp[i]=window/maxPts; if i<k add dp[i]
          to window; if i-maxPts still <k remove it.
        - Answer = sum(dp[k..n]).

        Complexity: O(n) time, O(n) space.
        """
        if k == 0 or n >= k + maxPts - 1:
            return 1.0
        dp = [0.0] * (n + 1)
        dp[0] = 1.0
        window = 1.0
        for i in range(1, n + 1):
            dp[i] = window / maxPts
            if i < k:
                window += dp[i]
            if i - maxPts >= 0 and i - maxPts < k:
                window -= dp[i - maxPts]
        return sum(dp[k :])
# @lc code=end
