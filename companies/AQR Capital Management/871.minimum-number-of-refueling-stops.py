#
# @lc app=leetcode id=871 lang=python3
#
# [871] Minimum Number of Refueling Stops
#
# https://leetcode.com/problems/minimum-number-of-refueling-stops/description/
#
# algorithms
# Hard (41.72%)
# Likes:    4926
# Dislikes: 95
# Total Accepted:    173K
# Total Submissions: 415K
# Testcase Example:  "1"
#
# A car travels from a starting position to a destination which is target miles
# east of the starting position.
#
# There are gas stations along the way. The gas stations are represented as an
# array stations where stations[i] = [position_i, fuel_i] indicates that the
# i^th gas station is position_i miles east of the starting position and has
# fuel_i liters of gas.
#
# The car starts with an infinite tank of gas, which initially has startFuel
# liters of fuel in it. It uses one liter of gas per one mile that it drives.
# When the car reaches a gas station, it may stop and refuel, transferring all
# the gas from the station into the car.
#
# Return the minimum number of refueling stops the car must make in order to
# reach its destination. If it cannot reach the destination, return -1.
#
# Note that if the car reaches a gas station with 0 fuel left, the car can
# still refuel there. If the car reaches the destination with 0 fuel left, it
# is still considered to have arrived.
#
# Example 1:
#
# Input: target = 1, startFuel = 1, stations = []
# Output: 0
# Explanation: We can reach the target without refueling.
#
# Example 2:
#
# Input: target = 100, startFuel = 1, stations = [[10,100]]
# Output: -1
# Explanation: We can not reach the target (or even the first gas station).
#
# Example 3:
#
# Input: target = 100, startFuel = 10, stations =
# [[10,60],[20,30],[30,30],[60,40]]
# Output: 2
# Explanation: We start with 10 liters of fuel.
# We drive to position 10, expending 10 liters of fuel. We refuel from 0 liters
# to 60 liters of gas.
# Then, we drive from position 10 to position 60 (expending 50 liters of fuel),
# and refuel from 10 liters to 50 liters of gas. We then drive to and reach the
# target.
# We made 2 refueling stops along the way, so we return 2.
#
# Constraints:
#
# 1 <= target, startFuel <= 10^9
#
# 0 <= stations.length <= 500
#
# 1 <= position_i < position_i+1 < target
#
# 1 <= fuel_i < 10^9
#

# @lc code=start
import heapq
from typing import List


class Solution:
    def minRefuelStops(self, target: int, startFuel: int, stations: List[List[int]]) -> int:
        """
        Interview explanation:
        Drive as far as current fuel allows; when short, retrospectively pick
        the largest past station (max-heap) — greedy optimal stop count.

        Algorithm (heap):
        - fuel=startFuel, i=0, stops=0, maxheap of passed station fuels.
        - While fuel < target: while stations reachable, push fuel. If heap
          empty return -1; else pop largest, add fuel, stops++.

        Complexity: O(n log n) time, O(n) space.
        """
        pq: List[int] = []
        stations = stations + [[target, 0]]
        ans = prev = 0
        fuel = startFuel
        for pos, gas in stations:
            fuel -= pos - prev
            while fuel < 0 and pq:
                fuel += -heapq.heappop(pq)
                ans += 1
            if fuel < 0:
                return -1
            heapq.heappush(pq, -gas)
            prev = pos
        return ans

    def minRefuelStops_dp(self, target: int, startFuel: int, stations: List[List[int]]) -> int:
        """
        Interview explanation:
        Alternate classic DP: dp[t] = farthest reach with exactly t refuels.
        For each station i, update dp backward: if dp[t]>=pos, can add gas.

        Algorithm:
        - dp[0]=startFuel; for each station, for t=i..0: if dp[t]>=pos:
          dp[t+1]=max(dp[t+1], dp[t]+gas).
        - Smallest t with dp[t]>=target.

        Complexity: O(n^2) time, O(n) space.
        """
        n = len(stations)
        dp = [0] * (n + 1)
        dp[0] = startFuel
        for i, (pos, gas) in enumerate(stations):
            for t in range(i, -1, -1):
                if dp[t] >= pos:
                    dp[t + 1] = max(dp[t + 1], dp[t] + gas)
        for t, reach in enumerate(dp):
            if reach >= target:
                return t
        return -1
# @lc code=end

