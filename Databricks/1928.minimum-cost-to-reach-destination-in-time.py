#
# @lc app=leetcode id=1928 lang=python3
#
# [1928] Minimum Cost to Reach Destination in Time
#
# https://leetcode.com/problems/minimum-cost-to-reach-destination-in-time/description/
#
# algorithms
# Hard (42.14%)
# Likes:    1003
# Dislikes: 23
# Total Accepted:    42.3K
# Total Submissions: 100K
# Testcase Example:  "30"
#
# There is a country of n cities numbered from 0 to n - 1 where all the cities
# are connected by bi-directional roads. The roads are represented as a 2D
# integer array edges where edges[i] = [x_i, y_i, time_i] denotes a road
# between cities x_i and y_i that takes time_i minutes to travel. There may be
# multiple roads of differing travel times connecting the same two cities, but
# no road connects a city to itself.
#
# Each time you pass through a city, you must pay a passing fee. This is
# represented as a 0-indexed integer array passingFees of length n where
# passingFees[j] is the amount of dollars you must pay when you pass through
# city j.
#
# In the beginning, you are at city 0 and want to reach city n - 1 in maxTime
# minutes or less. The cost of your journey is the summation of passing fees
# for each city that you passed through at some moment of your journey
# (including the source and destination cities).
#
# Given maxTime, edges, and passingFees, return the minimum cost to complete
# your journey, or -1 if you cannot complete it within maxTime minutes.
#
# Example 1:
#
# Input: maxTime = 30, edges =
# [[0,1,10],[1,2,10],[2,5,10],[0,3,1],[3,4,10],[4,5,15]], passingFees =
# [5,1,2,20,20,3]
# Output: 11
# Explanation: The path to take is 0 -> 1 -> 2 -> 5, which takes 30 minutes and
# has $11 worth of passing fees.
#
# Example 2:
#
# Input: maxTime = 29, edges =
# [[0,1,10],[1,2,10],[2,5,10],[0,3,1],[3,4,10],[4,5,15]], passingFees =
# [5,1,2,20,20,3]
# Output: 48
# Explanation: The path to take is 0 -> 3 -> 4 -> 5, which takes 26 minutes and
# has $48 worth of passing fees.
# You cannot take path 0 -> 1 -> 2 -> 5 since it would take too long.
#
# Example 3:
#
# Input: maxTime = 25, edges =
# [[0,1,10],[1,2,10],[2,5,10],[0,3,1],[3,4,10],[4,5,15]], passingFees =
# [5,1,2,20,20,3]
# Output: -1
# Explanation: There is no way to reach city 5 from city 0 within 25 minutes.
#
# Constraints:
#
# 1 <= maxTime <= 1000
#
# n == passingFees.length
#
# 2 <= n <= 1000
#
# n - 1 <= edges.length <= 1000
#
# 0 <= x_i, y_i <= n - 1
#
# 1 <= time_i <= 1000
#
# 1 <= passingFees[j] <= 1000
#
# The graph may contain multiple edges between two nodes.
#
# The graph does not contain self loops.
#

# @lc code=start
from typing import List
import heapq
from collections import defaultdict


class Solution:
    def minCost(self, maxTime: int, edges: List[List[int]], passingFees: List[int]) -> int:
        """
        Interview explanation:
        Min total passing fees to reach city n-1 with travel time ≤ maxTime.
        Pay fee on every city including start. Optimal DP over spent time.

        Algorithm:
        - Delegate to time-layered DP (classic optimal for constraints).

        Complexity: O(maxTime * (V+E)) time, O(maxTime * V) space.
        """
        return self.minCost_dp(maxTime, edges, passingFees)

    def minCost_dp(self, maxTime: int, edges: List[List[int]], passingFees: List[int]) -> int:
        """
        Interview explanation:
        Classic optimal DP: dp[t][u] = min fee to reach u using exactly time t.

        Algorithm:
        - dp[0][0]=fee[0]; for t,u relax edges to nt=t+w; answer min_t dp[t][n-1].

        Complexity: O(maxTime*(V+E)) time, O(maxTime*V) space.
        """
        n = len(passingFees)
        g = defaultdict(list)
        for u, v, t in edges:
            g[u].append((v, t))
            g[v].append((u, t))
        INF = 10**18
        dp = [[INF] * n for _ in range(maxTime + 1)]
        dp[0][0] = passingFees[0]
        for t in range(maxTime + 1):
            for u in range(n):
                cur = dp[t][u]
                if cur == INF:
                    continue
                for v, w in g[u]:
                    nt = t + w
                    if nt <= maxTime:
                        nf = cur + passingFees[v]
                        if nf < dp[nt][v]:
                            dp[nt][v] = nf
        ans = min(dp[t][n - 1] for t in range(maxTime + 1))
        return -1 if ans >= INF else ans

    def minCost_dijkstra(self, maxTime: int, edges: List[List[int]], passingFees: List[int]) -> int:
        """
        Interview explanation:
        Alternate: Dijkstra on fee with state (node,time); prune dominated
        (worse fee and worse/equal time).

        Algorithm:
        - PQ (fee,time,node); best[node]=min time for any path popped by fee order
          is insufficient alone — store best_fee[node][time] sparsely via best
          time array only when fee is primary key: first pop of (n-1) wins, and
          reopen node when finding smaller time (even with higher fee already in
          queue). Use min_time[u] prune only for equal-fee exploration; keep
          full: if nt < min_time[u], update and push.

        Complexity: O(E log E) typical with pruning.
        """
        n = len(passingFees)
        g = defaultdict(list)
        for u, v, t in edges:
            g[u].append((v, t))
            g[v].append((u, t))
        min_time = [maxTime + 1] * n
        pq = [(passingFees[0], 0, 0)]
        min_time[0] = 0
        while pq:
            fee, time, u = heapq.heappop(pq)
            if u == n - 1:
                return fee
            if time > min_time[u]:
                continue
            for v, w in g[u]:
                nt = time + w
                if nt < min_time[v] and nt <= maxTime:
                    min_time[v] = nt
                    heapq.heappush(pq, (fee + passingFees[v], nt, v))
        return -1
# @lc code=end
