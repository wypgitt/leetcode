#
# @lc app=leetcode id=1883 lang=python3
#
# [1883] Minimum Skips to Arrive at Meeting On Time
#
# https://leetcode.com/problems/minimum-skips-to-arrive-at-meeting-on-time/description/
#
# algorithms
# Hard (38.91%)
# Likes:    355
# Dislikes: 54
# Total Accepted:    9.0K
# Total Submissions: 23.2K
# Testcase Example:  "[1,3,2]"
#
# You are given an integer hoursBefore, the number of hours you have to travel
# to your meeting. To arrive at your meeting, you have to travel through n
# roads. The road lengths are given as an integer array dist of length n, where
# dist[i] describes the length of the i^th road in kilometers. In addition, you
# are given an integer speed, which is the speed (in km/h) you will travel at.
#
# After you travel road i, you must rest and wait for the next integer hour
# before you can begin traveling on the next road. Note that you do not have to
# rest after traveling the last road because you are already at the meeting.
#
# For example, if traveling a road takes 1.4 hours, you must wait until the 2
# hour mark before traveling the next road. If traveling a road takes exactly 2
# hours, you do not need to wait.
#
# However, you are allowed to skip some rests to be able to arrive on time,
# meaning you do not need to wait for the next integer hour. Note that this
# means you may finish traveling future roads at different hour marks.
#
# For example, suppose traveling the first road takes 1.4 hours and traveling
# the second road takes 0.6 hours. Skipping the rest after the first road will
# mean you finish traveling the second road right at the 2 hour mark, letting
# you start traveling the third road immediately.
#
# Return the minimum number of skips required to arrive at the meeting on time,
# or -1 if it is impossible.
#
# Example 1:
#
# Input: dist = [1,3,2], speed = 4, hoursBefore = 2
# Output: 1
# Explanation:
# Without skipping any rests, you will arrive in (1/4 + 3/4) + (3/4 + 1/4) +
# (2/4) = 2.5 hours.
# You can skip the first rest to arrive in ((1/4 + 0) + (3/4 + 0)) + (2/4) =
# 1.5 hours.
# Note that the second rest is shortened because you finish traveling the
# second road at an integer hour due to skipping the first rest.
#
# Example 2:
#
# Input: dist = [7,3,5,5], speed = 2, hoursBefore = 10
# Output: 2
# Explanation:
# Without skipping any rests, you will arrive in (7/2 + 1/2) + (3/2 + 1/2) +
# (5/2 + 1/2) + (5/2) = 11.5 hours.
# You can skip the first and third rest to arrive in ((7/2 + 0) + (3/2 + 0)) +
# ((5/2 + 0) + (5/2)) = 10 hours.
#
# Example 3:
#
# Input: dist = [7,3,5,5], speed = 1, hoursBefore = 10
# Output: -1
# Explanation: It is impossible to arrive at the meeting on time even if you
# skip all the rests.
#
# Constraints:
#
# n == dist.length
#
# 1 <= n <= 1000
#
# 1 <= dist[i] <= 10^5
#
# 1 <= speed <= 10^6
#
# 1 <= hoursBefore <= 10^7
#

# @lc code=start
from typing import List


class Solution:
    def minSkips(self, dist: List[int], speed: int, hoursBefore: int) -> int:
        """
        Interview explanation:
        n roads; after each road except the last, time ceils to an integer hour
        unless you skip that rest. Min skips so total time ≤ hoursBefore.

        Algorithm (DP):
        - dp[j] = min distance-units after roads before last with j skips
          (rest ⇒ round up to multiple of speed).
        - For each non-last road: rest → ceil((dp[j]+d)/speed)*speed; skip → +d.
        - Feasible if dp[j] + dist[-1] ≤ hoursBefore * speed.

        Complexity: O(n^2) time/space.
        """
        n = len(dist)
        INF = 10**18
        dp = [INF] * n
        dp[0] = 0
        for i in range(n - 1):
            d = dist[i]
            ndp = [INF] * n
            for j in range(i + 1):
                if dp[j] >= INF:
                    continue
                t = dp[j] + d
                ndp[j] = min(ndp[j], ((t + speed - 1) // speed) * speed)
                if j + 1 < n:
                    ndp[j + 1] = min(ndp[j + 1], t)
            dp = ndp
        limit = hoursBefore * speed
        for j in range(n):
            if dp[j] + dist[-1] <= limit:
                return j
        return -1
# @lc code=end
