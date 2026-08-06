#
# @lc app=leetcode id=1094 lang=python3
#
# [1094] Car Pooling
#
# https://leetcode.com/problems/car-pooling/description/
#
# algorithms
# Medium (56.46%)
# Likes:    4890
# Dislikes: 126
# Total Accepted:    346K
# Total Submissions: 612K
# Testcase Example:  "[[2,1,5],[3,3,7]]"
#
# There is a car with capacity empty seats. The vehicle only drives east (i.e.,
# it cannot turn around and drive west).
#
# You are given the integer capacity and an array trips where trips[i] =
# [numPassengers_i, from_i, to_i] indicates that the i^th trip has
# numPassengers_i passengers and the locations to pick them up and drop them
# off are from_i and to_i respectively. The locations are given as the number
# of kilometers due east from the car's initial location.
#
# Return true if it is possible to pick up and drop off all passengers for all
# the given trips, or false otherwise.
#
# Example 1:
#
# Input: trips = [[2,1,5],[3,3,7]], capacity = 4
# Output: false
#
# Example 2:
#
# Input: trips = [[2,1,5],[3,3,7]], capacity = 5
# Output: true
#
# Constraints:
#
# 1 <= trips.length <= 1000
#
# trips[i].length == 3
#
# 1 <= numPassengers_i <= 100
#
# 0 <= from_i < to_i <= 1000
#
# 1 <= capacity <= 10^5
#

# @lc code=start
from typing import List


class Solution:
    def carPooling(self, trips: List[List[int]], capacity: int) -> bool:
        """
        Interview explanation:
        Track passenger deltas at pickup/dropoff locations. Sweep left→right;
        if load ever exceeds capacity, impossible.

        Algorithm (diff array):
        - diff[from] += num; diff[to] -= num (locations ≤1000).
        - prefix sum; check ≤ capacity.

        Complexity: O(N + L) with L=1001, O(L) space.
        """
        diff = [0] * 1001
        for num, frm, to in trips:
            diff[frm] += num
            diff[to] -= num
        cur = 0
        for d in diff:
            cur += d
            if cur > capacity:
                return False
        return True

    def carPooling_sort(self, trips: List[List[int]], capacity: int) -> bool:
        """
        Interview explanation:
        Alternate classic: create (+num at from) and (-num at to) events;
        sort by location (drops before picks at same spot), scan load.

        Algorithm (sort events):
        - events = [(from,+num),(to,-num)]; sort by (loc, delta).
        - Accumulate; fail if > capacity.

        Complexity: O(n log n) time, O(n) space.
        """
        events = []
        for num, frm, to in trips:
            events.append((frm, num))
            events.append((to, -num))
        events.sort(key=lambda e: (e[0], e[1]))
        cur = 0
        for _, delta in events:
            cur += delta
            if cur > capacity:
                return False
        return True
# @lc code=end
