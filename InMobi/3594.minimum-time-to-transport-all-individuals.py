#
# @lc app=leetcode id=3594 lang=python3
#
# [3594] Minimum Time to Transport All Individuals
#
# https://leetcode.com/problems/minimum-time-to-transport-all-individuals/description/
#
# algorithms
# Hard (27.65%)
# Likes:    42
# Dislikes: 6
# Total Accepted:    3.7K
# Total Submissions: 13.4K
# Testcase Example:  "1\n1\n2\n[5]\n[1.0,1.3]"
#
#
# You are given n individuals at a base camp who need to cross a river to
# reach a destination using a single boat. The boat can carry at most k
# people at a time. The trip is affected by environmental conditions that
# vary cyclically over m stages.
#
# Each stage j has a speed multiplier mul[j]:
#
# If mul[j] > 1, the trip slows down.
#
# If mul[j] < 1, the trip speeds up.
#
# Each individual i has a rowing strength represented by time[i], the time
# (in minutes) it takes them to cross alone in neutral conditions.
#
# Rules:
#
# A group g departing at stage j takes time equal to the maximum time[i]
# among its members, multiplied by mul[j] minutes to reach the
# destination.
#
# After the group crosses the river in time d, the stage advances by
# floor(d) % m steps.
#
# If individuals are left behind, one person must return with the boat.
# Let r be the index of the returning person, the return takes time[r] ×
# mul[current_stage], defined as return_time, and the stage advances by
# floor(return_time) % m.
#
# Return the minimum total time required to transport all individuals. If
# it is not possible to transport all individuals to the destination,
# return -1.
#
# Example 1:
#
# Input: n = 1, k = 1, m = 2, time = [5], mul = [1.0,1.3]
#
# Output: 5.00000
#
# Explanation:
#
# Individual 0 departs from stage 0, so crossing time = 5 × 1.00 = 5.00
# minutes.
#
# All team members are now at the destination. Thus, the total time taken
# is 5.00 minutes.
#
# Example 2:
#
# Input: n = 3, k = 2, m = 3, time = [2,5,8], mul = [1.0,1.5,0.75]
#
# Output: 14.50000
#
# Explanation:
#
# The optimal strategy is:
#
# Send individuals 0 and 2 from the base camp to the destination from
# stage 0. The crossing time is max(2, 8) × mul[0] = 8 × 1.00 = 8.00
# minutes. The stage advances by floor(8.00) % 3 = 2, so the next stage is
# (0 + 2) % 3 = 2.
#
# Individual 0 returns alone from the destination to the base camp from
# stage 2. The return time is 2 × mul[2] = 2 × 0.75 = 1.50 minutes. The
# stage advances by floor(1.50) % 3 = 1, so the next stage is (2 + 1) % 3
# = 0.
#
# Send individuals 0 and 1 from the base camp to the destination from
# stage 0. The crossing time is max(2, 5) × mul[0] = 5 × 1.00 = 5.00
# minutes. The stage advances by floor(5.00) % 3 = 2, so the final stage
# is (0 + 2) % 3 = 2.
#
# All team members are now at the destination. The total time taken is
# 8.00 + 1.50 + 5.00 = 14.50 minutes.
#
# Example 3:
#
# Input: n = 2, k = 1, m = 2, time = [10,10], mul = [2.0,2.0]
#
# Output: -1.00000
#
# Explanation:
#
# Since the boat can only carry one person at a time, it is impossible to
# transport both individuals as one must always return. Thus, the answer
# is -1.00.
#
# Constraints:
#
# 1 <= n == time.length <= 12
#
# 1 <= k <= 5
#
# 1 <= m <= 5
#
# 1 <= time[i] <= 100
#
# m == mul.length
#
# 0.5 <= mul[i] <= 2.0
#

# @lc code=start

import heapq
from typing import List


class Solution:
    def minTime(
        self, n: int, k: int, m: int, time: List[int], mul: List[float]
    ) -> float:
        """
        Interview explanation:
        Classic boat crossing with stage multipliers. State =
        (boat_side, stage, bitmask of people still at camp). Dijkstra over
        subset moves of size ≤ k (forward) or single returners.

        Algorithm:
        - Precompute max time per nonempty mask.
        - dist[side][stage][mask]; start all-at-camp, boat at camp, stage 0.
        - Expand forward submasks / return singles; stage += floor(t) % m.

        Complexity: O(m · 3^n log(m·3^n)) time, O(m · 2^n) space.
        """
        full = (1 << n) - 1
        max_t = [0] * (1 << n)
        for mask in range(1, 1 << n):
            bit = mask.bit_length() - 1
            max_t[mask] = max(time[bit], max_t[mask ^ (1 << bit)])

        pop = [0] * (1 << n)
        for mask in range(1, 1 << n):
            pop[mask] = pop[mask >> 1] + (mask & 1)

        INF = float("inf")
        dist = [[[INF] * (1 << n) for _ in range(m)] for _ in range(2)]
        dist[0][0][full] = 0.0
        pq: List[tuple[float, int, int, int]] = [(0.0, 0, 0, full)]

        while pq:
            d, side, stage, mask = heapq.heappop(pq)
            if d != dist[side][stage][mask]:
                continue
            if mask == 0:
                return d
            if side == 0:
                sub = mask
                while sub:
                    if pop[sub] <= k:
                        t = max_t[sub] * mul[stage]
                        ns = (stage + int(t)) % m
                        nmask = mask ^ sub
                        nd = d + t
                        if nd < dist[1][ns][nmask]:
                            dist[1][ns][nmask] = nd
                            heapq.heappush(pq, (nd, 1, ns, nmask))
                    sub = (sub - 1) & mask
            else:
                at_dest = full ^ mask
                b = at_dest
                while b:
                    lsb = b & -b
                    t = max_t[lsb] * mul[stage]
                    ns = (stage + int(t)) % m
                    nmask = mask | lsb
                    nd = d + t
                    if nd < dist[0][ns][nmask]:
                        dist[0][ns][nmask] = nd
                        heapq.heappush(pq, (nd, 0, ns, nmask))
                    b ^= lsb
        return -1.0
# @lc code=end
