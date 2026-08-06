#
# @lc app=leetcode id=1626 lang=python3
#
# [1626] Best Team With No Conflicts
#
# https://leetcode.com/problems/best-team-with-no-conflicts/description/
#
# algorithms
# Medium (50.8%)
# Likes:    3072
# Dislikes: 100
# Total Accepted:    102K
# Total Submissions: 201K
# Testcase Example:  "[1,3,5,10,15]"
#
# You are the manager of a basketball team. For the upcoming tournament, you
# want to choose the team with the highest overall score. The score of the team
# is the sum of scores of all the players in the team.
#
# However, the basketball team is not allowed to have conflicts. A conflict
# exists if a younger player has a strictly higher score than an older player.
# A conflict does not occur between players of the same age.
#
# Given two lists, scores and ages, where each scores[i] and ages[i] represents
# the score and age of the i^th player, respectively, return the highest
# overall score of all possible basketball teams.
#
# Example 1:
#
# Input: scores = [1,3,5,10,15], ages = [1,2,3,4,5]
# Output: 34
# Explanation: You can choose all the players.
#
# Example 2:
#
# Input: scores = [4,5,6,5], ages = [2,1,2,1]
# Output: 16
# Explanation: It is best to choose the last 3 players. Notice that you are
# allowed to choose multiple people of the same age.
#
# Example 3:
#
# Input: scores = [1,2,3,5], ages = [8,9,10,1]
# Output: 6
# Explanation: It is best to choose the first 3 players.
#
# Constraints:
#
# 1 <= scores.length, ages.length <= 1000
#
# scores.length == ages.length
#
# 1 <= scores[i] <= 10^6
#
# 1 <= ages[i] <= 1000
#

# @lc code=start
from typing import List


class Solution:
    def bestTeamScore(self, scores: List[int], ages: List[int]) -> int:
        """
        Interview explanation:
        Team score = sum scores with no conflict: younger with strictly higher score
        than older is forbidden. Sort by age then score; DP like LIS on scores.

        Algorithm (sort + DP):
        - players sorted (age, score). dp[i]=best team ending at i = score[i] +
          max dp[j] for j<i with score[j]<=score[i]; answer max dp.

        Complexity: O(n^2) time, O(n) space.
        """
        players = sorted(zip(ages, scores))
        n = len(players)
        dp = [0] * n
        ans = 0
        for i in range(n):
            dp[i] = players[i][1]
            for j in range(i):
                if players[j][1] <= players[i][1]:
                    dp[i] = max(dp[i], dp[j] + players[i][1])
            ans = max(ans, dp[i])
        return ans

    def bestTeamScore_fenwick(self, scores: List[int], ages: List[int]) -> int:
        """
        Interview explanation:
        Alternate optimized DP: after sorting by age, query max dp among scores
        <= current via Fenwick/BIT on compressed scores.

        Algorithm (BIT):
        - Sort (age,score); compress scores; BIT stores max dp by score rank;
          query prefix max then update.

        Complexity: O(n log n) time, O(n) space.
        """
        players = sorted(zip(ages, scores))
        vals = sorted(set(scores))
        rank = {v: i + 1 for i, v in enumerate(vals)}
        m = len(vals)
        bit = [0] * (m + 1)

        def query(i: int) -> int:
            res = 0
            while i:
                res = max(res, bit[i])
                i -= i & -i
            return res

        def update(i: int, val: int) -> None:
            while i <= m:
                bit[i] = max(bit[i], val)
                i += i & -i

        ans = 0
        for _, sc in players:
            best = query(rank[sc]) + sc
            update(rank[sc], best)
            ans = max(ans, best)
        return ans
# @lc code=end
