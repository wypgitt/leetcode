#
# @lc app=leetcode id=815 lang=python3
#
# [815] Bus Routes
#
# https://leetcode.com/problems/bus-routes/description/
#
# algorithms
# Hard (47.47%)
# Likes:    4762
# Dislikes: 137
# Total Accepted:    303K
# Total Submissions: 637K
# Testcase Example:  "[[1,2,7],[3,6,7]]"
#
# You are given an array routes representing bus routes where routes[i] is a
# bus route that the i^th bus repeats forever.
#
# For example, if routes[0] = [1, 5, 7], this means that the 0^th bus travels
# in the sequence 1 -> 5 -> 7 -> 1 -> 5 -> 7 -> 1 -> ... forever.
#
# You will start at the bus stop source (You are not on any bus initially), and
# you want to go to the bus stop target. You can travel between bus stops by
# buses only.
#
# Return the least number of buses you must take to travel from source to
# target. Return -1 if it is not possible.
#
# Example 1:
#
# Input: routes = [[1,2,7],[3,6,7]], source = 1, target = 6
# Output: 2
# Explanation: The best strategy is take the first bus to the bus stop 7, then
# take the second bus to the bus stop 6.
#
# Example 2:
#
# Input: routes = [[7,12],[4,5,15],[6],[15,19],[9,12,13]], source = 15, target
# = 12
# Output: -1
#
# Constraints:
#
# 1 <= routes.length <= 500.
#
# 1 <= routes[i].length <= 10^5
#
# All the values of routes[i] are unique.
#
# sum(routes[i].length) <= 10^5
#
# 0 <= routes[i][j] < 10^6
#
# 0 <= source, target < 10^6
#

# @lc code=start

from typing import List
from collections import defaultdict, deque


class Solution:
    def numBusesToDestination(self, routes: List[List[int]], source: int, target: int) -> int:
        """
        Interview explanation:
        Model buses as "nodes": riding one bus visits all its stops. BFS on
        buses (or stops with bus hops). Map stop → list of bus indices; BFS
        from source counting buses taken.

        Algorithm (BFS):
        - If source==target: 0. Build stop→buses. Queue stops with bus_count;
          when taking a bus, enqueue all its stops once per bus.

        Complexity: O(sum route lengths) time/space.
        """
        if source == target:
            return 0
        stop_to_buses = defaultdict(list)
        for i, route in enumerate(routes):
            for stop in route:
                stop_to_buses[stop].append(i)
        q = deque([(source, 0)])
        seen_stops = {source}
        seen_buses = set()
        while q:
            stop, buses = q.popleft()
            for b in stop_to_buses[stop]:
                if b in seen_buses:
                    continue
                seen_buses.add(b)
                for nxt in routes[b]:
                    if nxt == target:
                        return buses + 1
                    if nxt not in seen_stops:
                        seen_stops.add(nxt)
                        q.append((nxt, buses + 1))
        return -1
# @lc code=end
