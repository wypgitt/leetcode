#
# @lc app=leetcode id=4009 lang=python3
#
# [4009] Minimum Possible Maximum Waiting Time
#
# https://leetcode.com/problems/minimum-possible-maximum-waiting-time/description/
#
# algorithms
# Hard (27.91%)
# Likes:    13
# Dislikes: 12
# Total Accepted:    2.1K
# Total Submissions: 7.6K
# Testcase Example:  "[6,8,4,6,5]\r\n[16,13]\r"
#
#
# You are given an integer array demand, where demand[i] is the amount of
# fuel required by the i^th car.
#
# You are also given an integer array fuel of length 2. There are exactly
# two fuel dispensers, numbered 0 and 1, where fuel[j] is the initial
# amount of fuel available in dispenser j.
#
# Cars are allowed to start refueling in increasing index order. Car 0
# becomes allowed at time 0, and for each i > 0, car i becomes allowed
# exactly when car i - 1 starts refueling.
#
# The refueling process follows these rules:
#
# Each dispenser can serve at most one car at a time.
#
# When a car becomes allowed, you must choose a dispenser with at least
# demand[i] fuel remaining. If both dispensers have enough fuel remaining,
# you may choose either of them, regardless of when they become free.
#
# The car waits until the chosen dispenser becomes free and starts
# refueling immediately. It cannot switch dispensers or intentionally wait
# after the chosen dispenser becomes free.
#
# When a car starts refueling, the remaining fuel in the chosen dispenser
# decreases by demand[i], and the dispenser remains occupied for demand[i]
# seconds.
#
# Once started, refueling cannot be interrupted.
#
# If neither dispenser has at least demand[i] fuel remaining when car i
# becomes allowed, the process terminates and no further cars can be
# served.
#
# The waiting time of a car is the time between when it becomes allowed to
# start refueling and when it actually starts.
#
# Return the minimum possible value of the maximum waiting time among all
# served cars over all assignments that maximize the number of served
# cars. If no car can be served, return -1.
#
# Example 1:
#
# Input: demand = [6,8,4,6,5], fuel = [16,13]
#
# Output: 6
#
# Explanation:
#
# The following assignment serves all five cars:
#
#                         Car
#                         Becomes allowed at
#                         Starts refueling at
#                         Dispenser used
#                         Remaining fuel before start
#
#                         (dispenser 0, dispenser 1)
#                         Waiting time
#
#                         0
#                         0
#                         0
#                         0
#                         (16, 13)
#                         0
#
#                         1
#                         0
#                         0
#                         1
#                         (10, 13)
#                         0
#
#                         2
#                         0
#                         6
#                         0
#                         (10, 5)
#                         6
#
#                         3
#                         6
#                         10
#                         0
#                         (6, 5)
#                         4
#
#                         4
#                         10
#                         10
#                         1
#                         (0, 5)
#                         0
#
# Thus, all five cars are served, and the maximum waiting time is 6.
#
# To serve all five cars, dispenser 0 must serve the cars with demands 6,
# 4, and 6, while dispenser 1 must serve the cars with demands 8 and 5.
# Therefore, car 2 must wait until time 6 for dispenser 0 to become free,
# so no assignment serving all five cars can have a maximum waiting time
# less than 6.
#
# Example 2:
#
# Input: demand = [10,15], fuel = [12,17]
#
# Output: 0
#
# Explanation:
#
# At time 0, Car 0 becomes allowed and starts refuelling using dispenser
# 0.
#
# Car 1 becomes allowed at time 0 (when Car 0 starts) and immediately
# starts refuelling using dispenser 1.
#
# Both cars start without waiting, so the maximum waiting time is 0.
#
# Example 3:
#
# Input: demand = [10,5], fuel = [8,8]
#
# Output: -1
#
# Explanation:
#
# At time 0, Car 0 becomes allowed. However, neither dispenser has enough
# fuel to serve it, so the process terminates immediately.
#
# No car is served, so the answer is -1.
#
# Constraints:
#
# 1 <= demand.length <= 50
#
# 1 <= demand[i] <= 20
#
# fuel.length == 2
#
# 1 <= fuel[i] <= 50
#

# @lc code=start
from typing import List


class Solution:
    def minMaxWaitingTime(self, demand: List[int], fuel: List[int]) -> int:
        """
        Interview explanation:
        Assign each car to one of two fuel-limited dispensers in order,
        maximizing how many cars can be served, then among those assignments
        minimize the maximum waiting time.

        Algorithm:
        - DP over fuel usage finds the longest feasible prefix length L.
        - Binary search max-wait w; DP state (last dispenser, busy gap of the
          other, fuel used on dispenser 0) checks whether the L-prefix is
          schedulable with wait ≤ w.

        Complexity: O(L · D · F · log D) time, O(D · F) space
        (D=max demand, F=fuel[0], L≤n≤50).
        """
        def find_max_served() -> int:
            dp = [False] * (fuel[0] + 1)
            dp[0] = True
            total = 0
            for i, x in enumerate(demand):
                new_dp = [False] * (fuel[0] + 1)
                for used0, ok in enumerate(dp):
                    if not ok:
                        continue
                    if used0 + x <= fuel[0]:
                        new_dp[used0 + x] = True
                    if total - used0 + x <= fuel[1]:
                        new_dp[used0] = True
                if not any(new_dp):
                    return i
                dp = new_dp
                total += x
            return len(demand)

        def check(w: int) -> bool:
            dp = [[[False] * (fuel[0] + 1) for _ in range(mx + 1)] for _ in range(2)]
            dp[0][0][0] = True
            total = 0
            for i in range(l):
                new_dp = [[[False] * (fuel[0] + 1) for _ in range(mx + 1)] for _ in range(2)]
                prev = demand[i - 1] if i else 0
                for last in range(2):
                    for gap in range(mx + 1):
                        for used0 in range(fuel[0] + 1):
                            if not dp[last][gap][used0]:
                                continue
                            # stay on same dispenser if previous service ≤ w
                            if prev <= w:
                                ng = max(gap - prev, 0)
                                if last == 0:
                                    if used0 + demand[i] <= fuel[0]:
                                        new_dp[last][ng][used0 + demand[i]] = True
                                elif total - used0 + demand[i] <= fuel[1]:
                                    new_dp[last][ng][used0] = True
                            # switch if the other dispenser's remaining busy ≤ w
                            if gap <= w:
                                ng = max(prev - gap, 0)
                                nxt = last ^ 1
                                if nxt == 0:
                                    if used0 + demand[i] <= fuel[0]:
                                        new_dp[nxt][ng][used0 + demand[i]] = True
                                elif total - used0 + demand[i] <= fuel[1]:
                                    new_dp[nxt][ng][used0] = True
                dp = new_dp
                total += demand[i]
            return any(ok for matrix in dp for row in matrix for ok in row)

        l = find_max_served()
        if not l:
            return -1
        mx = max(demand)
        lo, hi = 0, mx
        while lo < hi:
            mid = (lo + hi) >> 1
            if check(mid):
                hi = mid
            else:
                lo = mid + 1
        return lo
# @lc code=end
