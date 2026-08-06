#
# @lc app=leetcode id=3733 lang=python3
#
# [3733] Minimum Time to Complete All Deliveries
#
# https://leetcode.com/problems/minimum-time-to-complete-all-deliveries/description/
#
# algorithms
# Medium (35.66%)
# Likes:    186
# Dislikes: 15
# Total Accepted:    15.4K
# Total Submissions: 43.2K
# Testcase Example:  "[3,1]\n[2,3]"
#
#
# You are given two integer arrays of size 2: d = [d_1, d_2] and r = [r_1,
# r_2].
#
# Two delivery drones are tasked with completing a specific number of
# deliveries. Drone i must complete d_i deliveries.
#
# Each delivery takes exactly one hour and only one drone can make a
# delivery at any given hour.
#
# Additionally, both drones require recharging at specific intervals
# during which they cannot make deliveries. Drone i must recharge every
# r_i hours (i.e. at hours that are multiples of r_i).
#
# Return an integer denoting the minimum total time (in hours) required to
# complete all deliveries.
#
# Example 1:
#
# Input: d = [3,1], r = [2,3]
#
# Output: 5
#
# Explanation:
#
# The first drone delivers at hours 1, 3, 5 (recharges at hours 2, 4).
#
# The second drone delivers at hour 2 (recharges at hour 3).
#
# Example 2:
#
# Input: d = [1,3], r = [2,2]
#
# Output: 7
#
# Explanation:
#
# The first drone delivers at hour 3 (recharges at hours 2, 4, 6).
#
# The second drone delivers at hours 1, 5, 7 (recharges at hours 2, 4, 6).
#
# Example 3:
#
# Input: d = [2,1], r = [3,4]
#
# Output: 3
#
# Explanation:
#
# The first drone delivers at hours 1, 2 (recharges at hour 3).
#
# The second drone delivers at hour 3.
#
# Constraints:
#
# d = [d_1, d_2]
#
# 1 <= d_i <= 10^9
#
# r = [r_1, r_2]
#
# 2 <= r_i <= 3 * 10^4
#

# @lc code=start
from math import lcm
from typing import List


class Solution:
    def minimumTime(self, d: List[int], r: List[int]) -> int:
        """
        Interview explanation:
        Binary search the total hours T. At time T, drone i has T - floor(T/r_i)
        free hours; hours multiple of lcm(r1,r2) are unusable by either.

        Algorithm:
        - Feasible iff T - T//r_i >= d_i for both and T - T//lcm >= d1+d2.
        - Search T in [sum(d), 2*sum(d)].

        Complexity: O(log D) time, O(1) space.
        """
        L = lcm(r[0], r[1])

        def ok(t: int) -> bool:
            return (
                t - t // r[0] >= d[0]
                and t - t // r[1] >= d[1]
                and t - t // L >= d[0] + d[1]
            )

        lo, hi = sum(d), sum(d) * 2
        while lo < hi:
            mid = (lo + hi) // 2
            if ok(mid):
                hi = mid
            else:
                lo = mid + 1
        return lo

    def minimumTime_scan(self, d: List[int], r: List[int]) -> int:
        """
        Interview explanation:
        Alternate: same feasibility check with an explicit expanding upper bound.

        Algorithm:
        - Double hi until feasible, then binary search.

        Complexity: O(log D) time, O(1) space.
        """
        L = lcm(r[0], r[1])

        def ok(t: int) -> bool:
            return (
                t - t // r[0] >= d[0]
                and t - t // r[1] >= d[1]
                and t - t // L >= d[0] + d[1]
            )

        lo, hi = 1, max(sum(d), 1)
        while not ok(hi):
            lo, hi = hi, hi * 2
        while lo < hi:
            mid = (lo + hi) // 2
            if ok(mid):
                hi = mid
            else:
                lo = mid + 1
        return lo
# @lc code=end

