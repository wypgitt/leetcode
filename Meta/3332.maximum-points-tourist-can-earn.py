#
# @lc app=leetcode id=3332 lang=python3
#
# [3332] Maximum Points Tourist Can Earn
#
# https://leetcode.com/problems/maximum-points-tourist-can-earn/description/
#
# algorithms
# Medium (47.33%)
# Likes:    98
# Dislikes: 16
# Total Accepted:    16.1K
# Total Submissions: 34.1K
# Testcase Example:  "2\n1\n[[2,3]]\n[[0,2],[1,0]]"
#
#
# You are given two integers, n and k, along with two 2D integer arrays,
# stayScore and travelScore.
#
# A tourist is visiting a country with n cities, where each city is
# directly connected to every other city. The tourist's journey consists
# of exactly k 0-indexed days, and they can choose any city as their
# starting point.
#
# Each day, the tourist has two choices:
#
# Stay in the current city: If the tourist stays in their current city
# curr during day i, they will earn stayScore[i][curr] points.
#
# Move to another city: If the tourist moves from their current city curr
# to city dest, they will earn travelScore[curr][dest] points.
#
# Return the maximum possible points the tourist can earn.
#
# Example 1:
#
# Input: n = 2, k = 1, stayScore = [[2,3]], travelScore = [[0,2],[1,0]]
#
# Output: 3
#
# Explanation:
#
# The tourist earns the maximum number of points by starting in city 1 and
# staying in that city.
#
# Example 2:
#
# Input: n = 3, k = 2, stayScore = [[3,4,2],[2,1,2]], travelScore =
# [[0,2,1],[2,0,4],[3,2,0]]
#
# Output: 8
#
# Explanation:
#
# The tourist earns the maximum number of points by starting in city 1,
# staying in that city on day 0, and traveling to city 2 on day 1.
#
# Constraints:
#
# 1 <= n <= 200
#
# 1 <= k <= 200
#
# n == travelScore.length == travelScore[i].length == stayScore[i].length
#
# k == stayScore.length
#
# 1 <= stayScore[i][j] <= 100
#
# 0 <= travelScore[i][j] <= 100
#
# travelScore[i][i] == 0
#

# @lc code=start

from typing import List


class Solution:
    def maxScore(
        self, n: int, k: int, stayScore: List[List[int]], travelScore: List[List[int]]
    ) -> int:
        """
        Interview explanation:
        Exactly k days; each day stay in current city or travel to another.
        Maximize total points from an arbitrary start city.

        Algorithm:
        - dp[c] = best score ending in city c after the days processed so far.
        - Transition: stay -> dp[c]+stayScore[day][c]; travel c->d ->
          dp[c]+travelScore[c][d].
        - Alternate: precompute best arrival into each city from any origin.

        Complexity: O(k n^2) time, O(n) space.
        """
        dp = [0] * n
        for day in range(k):
            ndp = [0] * n
            best_to = [0] * n
            for dest in range(n):
                best = 0
                for src in range(n):
                    if src == dest:
                        continue
                    best = max(best, dp[src] + travelScore[src][dest])
                best_to[dest] = best
            for c in range(n):
                ndp[c] = max(dp[c] + stayScore[day][c], best_to[c])
            dp = ndp
        return max(dp)
# @lc code=end

