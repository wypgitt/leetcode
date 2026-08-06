#
# @lc app=leetcode id=2188 lang=python3
#
# [2188] Minimum Time to Finish the Race
#
# https://leetcode.com/problems/minimum-time-to-finish-the-race/description/
#
# algorithms
# Hard (43.52%)
# Likes:    611
# Dislikes: 30
# Total Accepted:    16.3K
# Total Submissions: 37.4K
# Testcase Example:  "[[2,3],[3,4]]\n5\n4"
#
# You are given a 0-indexed 2D integer array tires where tires[i] = [f_i, r_i]
# indicates that the i^th tire can finish its x^th successive lap in f_i *
# r_i^(x-1) seconds.
#
#
# For example, if f_i = 3 and r_i = 2, then the tire would finish its 1^st lap
# in 3 seconds, its 2^nd lap in 3 * 2 = 6 seconds, its 3^rd lap in 3 * 2^2 = 12
# seconds, etc.
#
# You are also given an integer changeTime and an integer numLaps.
#
# The race consists of numLaps laps and you may start the race with any tire.
# You have an unlimited supply of each tire and after every lap, you may change
# to any given tire (including the current tire type) if you wait changeTime
# seconds.
#
# Return the minimum time to finish the race.
#
#
#
# Example 1:
#
# Input: tires = [[2,3],[3,4]], changeTime = 5, numLaps = 4
# Output: 21
# Explanation:
# Lap 1: Start with tire 0 and finish the lap in 2 seconds.
# Lap 2: Continue with tire 0 and finish the lap in 2 * 3 = 6 seconds.
# Lap 3: Change tires to a new tire 0 for 5 seconds and then finish the lap in
# another 2 seconds.
# Lap 4: Continue with tire 0 and finish the lap in 2 * 3 = 6 seconds.
# Total time = 2 + 6 + 5 + 2 + 6 = 21 seconds.
# The minimum time to complete the race is 21 seconds.
#
# Example 2:
#
# Input: tires = [[1,10],[2,2],[3,4]], changeTime = 6, numLaps = 5
# Output: 25
# Explanation:
# Lap 1: Start with tire 1 and finish the lap in 2 seconds.
# Lap 2: Continue with tire 1 and finish the lap in 2 * 2 = 4 seconds.
# Lap 3: Change tires to a new tire 1 for 6 seconds and then finish the lap in
# another 2 seconds.
# Lap 4: Continue with tire 1 and finish the lap in 2 * 2 = 4 seconds.
# Lap 5: Change tires to tire 0 for 6 seconds then finish the lap in another 1
# second.
# Total time = 2 + 4 + 6 + 2 + 4 + 6 + 1 = 25 seconds.
# The minimum time to complete the race is 25 seconds.
#
#
#
# Constraints:
#
#
# 1 <= tires.length <= 10^5
#
#
# tires[i].length == 2
#
#
# 1 <= f_i, changeTime <= 10^5
#
#
# 2 <= r_i <= 10^5
#
#
# 1 <= numLaps <= 1000
#

# @lc code=start
from typing import List


class Solution:
    def minimumFinishTime(self, tires: List[List[int]], changeTime: int, numLaps: int) -> int:
        """
        Interview explanation:
        Each tire (fi, ri): lap j (0-index since last change) takes fi * ri^j.
        Changing tires costs changeTime (also before first? start with a tire,
        first choice free of prior change — but switching between stints pays
        changeTime). Minimize total time for numLaps.

        Algorithm:
        (precompute best without change + DP)
        - For each tire, compute consecutive-lap costs until worse than change;
          take min cost to run exactly k consecutive laps without changing.
        - dp[x] = min time for x laps: for k=1..max, dp[x]=min(dp[x-k] + without[k]
          + (changeTime if x-k>0 else 0)) — typically include change before each
          new stint except start: dp[i] = min over j < i of dp[j]+changeTime+best[i-j]
          with dp[0]=-changeTime trick or separate first.

        Complexity: O(numLaps * min(numLaps, 20) + tires*20) time.
        """
        # without[k] = min time to do k consecutive laps on one tire (no change)
        INF = 10**18
        without = [INF] * 18
        for f, r in tires:
            t = 0
            cur = f
            for k in range(1, 18):
                t += cur
                without[k] = min(without[k], t)
                if cur > changeTime + f:
                    break
                cur *= r

        # dp[0] = -changeTime so the first stint does not pay an initial change
        dp = [INF] * (numLaps + 1)
        dp[0] = -changeTime
        for i in range(1, numLaps + 1):
            for k in range(1, min(i + 1, 18)):
                if without[k] >= INF:
                    continue
                dp[i] = min(dp[i], dp[i - k] + changeTime + without[k])
        return dp[numLaps]
# @lc code=end
