#
# @lc app=leetcode id=3977 lang=python3
#
# [3977] Minimum Time to Reach Target With Limited Power
#
# https://leetcode.com/problems/minimum-time-to-reach-target-with-limited-power/description/
#
# algorithms
# Hard (41.09%)
# Likes:    64
# Dislikes: 4
# Total Accepted:    10.6K
# Total Submissions: 25.8K
# Testcase Example:  "5\n[[0,1,1],[1,4,1],[0,2,1],[2,3,1],[3,4,1]]\n4\n[2,3,1,1,1]\n0\n4"
#
#
# You are given a directed weighted graph with n nodes labeled from 0 to n
# - 1.
#
# The graph is represented by a 2D integer array edges, where edges[i] =
# [u_i, v_i, t_i] indicates a directed edge from node u_i to node v_i that
# takes t_i seconds to traverse.
#
# You are also given an integer power representing the initial available
# power, and an integer array cost of length n, where cost[u] represents
# the power required to forward the signal from node u through any one of
# its outgoing edges.
#
# You are given two integers source and target.
#
# The signal starts at source at time 0 with power units of power and
# follows these rules:
#
# The signal may traverse a directed edge from node u only if the
# remaining power is at least cost[u].
#
# No power is consumed when the signal arrives at a node, unless it later
# leaves that node by traversing another edge.
#
# When the signal is forwarded from node u, the remaining power is
# decreased by cost[u] units.
#
# Traversing an edge edges[i] = [u_i, v_i, t_i] increases the total time
# by t_i seconds.
#
# Return an integer array answer of size 2, where:
#
# answer[0] is the minimum time required for the signal to reach node
# target.
#
# answer[1] is the maximum remaining power among all paths that achieve
# answer[0].
#
# If the signal cannot reach target, return [-1, -1].
#
# Example 1:
#
# Input: n = 5, edges = [[0,1,1],[1,4,1],[0,2,1],[2,3,1],[3,4,1]], power =
# 4, cost = [2,3,1,1,1], source = 0, target = 4
#
# Output: [3,0]
#
# Explanation:
#
# The signal starts at node 0 with 4 units of power.
#
# The path 0 -> 1 -> 4 is not valid, because after leaving node 0, the
# signal has 2 units of power remaining, which is less than cost[1] = 3.
#
# The valid path 0 -> 2 -> 3 -> 4 takes a total time of 3.
#
# The total power consumed along this path is cost[0] + cost[2] + cost[3]
# = 4, leaving 0 remaining power.
#
# Hence, the answer is [3, 0].
#
# Example 2:
#
# Input: n = 3, edges = [[0,1,2],[1,2,2],[2,0,2]], power = 3, cost =
# [1,1,1], source = 1, target = 1
#
# Output: [0,3]
#
# Explanation:
#
# Since the source and target are the same node, no traversal is required.
#
# Hence, the minimum total time taken is 0, and no power is consumed.
#
# Therefore, the answer is [0, 3].
#
# Example 3:
#
# ​​​​​​​
#
# Input: n = 4, edges = [[0,1,3],[2,3,4]], power = 3, cost = [1,1,1,1],
# source = 0, target = 3
#
# Output: [-1,-1]
#
# Explanation:
#
# There is no valid path from source to target, therefore return [-1, -1].
#
# Constraints:
#
# 1 <= n <= 1000
#
# 0 <= edges.length <= 1000
#
# edges[i] = [u_i, v_i, t_i]
#
# 0 <= u_i, v_i <= n - 1
#
# 1 <= t_i <= 10^9
#
# 1 <= power <= 1000
#
# cost.length == n
#
# 1 <= cost[i] <= 2000
#
# 0 <= source, target <= n - 1
#

# @lc code=start

from heapq import heappop, heappush
from math import inf
from typing import List


class Solution:
    def minTimeMaxPower(
        self,
        n: int,
        edges: List[List[int]],
        power: int,
        cost: List[int],
        source: int,
        target: int,
    ) -> List[int]:
        """
        Interview explanation:
        State is (node, remaining_power). Minimize travel time, then maximize
        leftover power; Dijkstra with lexicographic (time, -power) works.

        Algorithm:
        - Leaving u costs cost[u] power and requires remaining >= cost[u].
        - Priority queue of (time, -power, node); first pop of target is optimal.
        - Track best time per (node, power); skip dominated states.

        Complexity: O((n*P + m*P) log(n*P)) time, O(n*P) space, P = power.
        """
        g = [[] for _ in range(n)]
        for u, v, t in edges:
            g[u].append((v, t))
        dist = [[inf] * (power + 1) for _ in range(n)]
        dist[source][power] = 0
        pq = [(0, -power, source)]
        while pq:
            d, p, u = heappop(pq)
            p = -p
            if u == target:
                return [d, p]
            if d > dist[u][p] or p < cost[u]:
                continue
            p -= cost[u]
            for v, t in g[u]:
                nd = d + t
                if nd < dist[v][p]:
                    dist[v][p] = nd
                    heappush(pq, (nd, -p, v))
        return [-1, -1]
# @lc code=end
