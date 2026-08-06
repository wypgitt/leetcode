#
# @lc app=leetcode id=774 lang=python3
#
# [774] Minimize Max Distance to Gas Station
#
# https://leetcode.com/problems/minimize-max-distance-to-gas-station/description/
#
# algorithms
# Hard (54.05%)
# Likes:    714
# Dislikes: 104
# Total Accepted:    38K
# Total Submissions: 70.4K
# Testcase Example:  "[1,2,3,4,5,6,7,8,9,10]\n9"
#
#
# You are given an integer array stations that represents the positions of
# the gas stations on the x-axis. You are also given an integer k.
#
# You should add k new gas stations. You can add the stations anywhere on
# the x-axis, and not necessarily on an integer position.
#
# Let penalty() be the maximum distance between adjacent gas stations
# after adding the k new stations.
#
# Return the smallest possible value of penalty(). Answers within 10^-6 of
# the actual answer will be accepted.
#
# Example 1:
#
# Input: stations = [1,2,3,4,5,6,7,8,9,10], k = 9
# Output: 0.50000
#
# Example 2:
#
# Input: stations = [23,24,36,39,46,56,57,65,84,98], k = 1
# Output: 14.00000
#
# Constraints:
#
# 10 <= stations.length <= 2000
#
# 0 <= stations[i] <= 10^8
#
# stations is sorted in a strictly increasing order.
#
# 1 <= k <= 10^6
#
# @lc code=start
from math import ceil
from typing import List


class Solution:
    def minmaxGasDist(self, stations: List[int], k: int) -> float:
        """
        Interview explanation:
        Premium. Add at most k new stations to minimize the maximum distance
        between adjacent stations. Binary search the answer D: for each gap,
        inserts needed = ceil(gap/D) - 1; feasible iff total inserts <= k.

        Algorithm:
        - lo = 0, hi = max adjacent gap.
        - While precision remains: mid = (lo+hi)/2; if can(mid): hi = mid
          else lo = mid.
        - Return hi (minimum feasible max distance).

        Complexity: O(n * log(range/eps)) time, O(1) space.
        """
        def can(d: float) -> bool:
            if d == 0:
                return False
            need = 0
            for i in range(1, len(stations)):
                gap = stations[i] - stations[i - 1]
                need += ceil(gap / d) - 1
            return need <= k

        hi = float(max(stations[i] - stations[i - 1] for i in range(1, len(stations))))
        if hi == 0:
            return 0.0
        lo = 0.0
        for _ in range(100):
            mid = (lo + hi) / 2
            if can(mid):
                hi = mid
            else:
                lo = mid
        return hi
# @lc code=end



