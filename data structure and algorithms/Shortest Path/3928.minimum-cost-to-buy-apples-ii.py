#
# @lc app=leetcode id=3928 lang=python3
#
# [3928] Minimum Cost to Buy Apples II
#
# https://leetcode.com/problems/minimum-cost-to-buy-apples-ii/description/
#
# algorithms
# Hard (31.94%)
# Likes:    51
# Dislikes: 2
# Total Accepted:    8K
# Total Submissions: 25.1K
# Testcase Example:  "2\n[8,3]\n[[0,1,1,2]]"
#
#
# You are given an integer n and an integer array prices of length n,
# where prices[i] is the price of apples at shop i.
#
# You are also given a 2D integer array roads, where roads[i] = [u_i, v_i,
# cost_i, tax_i] represents a bidirectional road:
#
# u_i and v_i are the shops connected by the road.
#
# cost_i is the cost to travel the road without carrying apples.
#
# tax_i is the multiplier applied to cost_i when traveling with apples.
#
# For each shop i, you can either:
#
# Buy apples locally at shop i for prices[i].
#
# Travel empty to any shop j using any number of roads, buy apples for
# prices[j], and return to shop i while carrying apples, paying cost * tax
# on each road used for the return trip.
#
# The forward path, where you travel empty, and the return path may be
# different.
#
# Return an integer array ans of length n, where ans[i] is the minimum
# total cost to buy apples starting from shop i.
#
# Example 1:
#
# Input: n = 2, prices = [8,3], roads = [[0,1,1,2]]
#
# Output: [6,3]
#
# Explanation:
#
#                         Shop i
#                         prices[i]
#                         Shop j
#                         prices[j]
#                         cost_i
#                         tax_i
#                         Travel cost
#                         Return cost
#                         Total
#                         Minimum
#
#                         0
#                         8
#                         1
#                         3
#                         1
#                         2
#                         1
#                         1 * 2 = 2
#                         1 + 2 + 3 = 6
#                         min(8, 6) = 6
#
#                         1
#                         3
#                         0
#                         8
#                         1
#                         2
#                         1
#                         1 * 2 = 2
#                         1 + 2 + 8 = 11
#                         min(3, 11) = 3
#
# Thus, the answer is [6, 3].
#
# Example 2:
#
# Input: n = 3, prices = [9,4,6], roads = [[0,1,1,3],[1,2,4,2]]
#
# Output: [8,4,6]
#
# Explanation:
#
# ​​​​​​​
#
#                         Shop i
#                         prices[i]
#                         Shop j
#                         prices[j]
#                         cost_i
#                         tax_i
#                         Travel cost
#                         Return cost
#                         Total
#                         Minimum
#
#                         0
#                         9
#                         1
#                         4
#                         1
#                         3
#                         1
#                         1 * 3 = 3
#                         1 + 3 + 4 = 8
#                         min(9, 8) = 8
#
#                         1
#                         4
#                         2
#                         6
#                         4
#                         2
#                         4
#                         4 * 2 = 8
#                         4 + 8 + 6 = 18
#                         min(4, 18) = 4
#
#                         2
#                         6
#                         1
#                         4
#                         4
#                         2
#                         4
#                         4 * 2 = 8
#                         4 + 8 + 4 = 16
#                         min(6, 16) = 6
#
# Thus, the answer is [8, 4, 6].
#
# Example 3:
#
# Input: n = 3, prices = [10,11,1], roads =
# [[0,2,1,3],[1,2,3,4],[0,1,5,2]]
#
# Output: [5,11,1]
#
# Explanation:
#
# ​​​​​​​​​​​​​​
#
#                         Shop i
#                         prices[i]
#                         Shop j
#                         prices[j]
#                         cost_i
#                         tax_i
#                         Travel cost
#                         Return cost
#                         Total
#                         Minimum
#
#                         0
#                         10
#                         2
#                         1
#                         1
#                         3
#                         1
#                         1 * 3 = 3
#                         1 + 3 + 1 = 5
#                         min(10, 5) = 5
#
#                         1
#                         11
#                         2
#                         1
#                         3
#                         4
#                         3
#                         3 * 4 = 12
#                         3 + 12 + 1 = 16
#                         min(11, 16) = 11
#
#                         2
#                         1
#                         0
#                         10
#                         1
#                         3
#                         1
#                         1 * 3 = 3
#                         1 + 3 + 10 = 14
#                         min(1, 14) = 1
#
# Thus, the answer is [5, 11, 1].
#
# Constraints:
#
# 1 <= n <= 1000
#
# prices.length == n
#
# 1 <= prices[i] <= 10^9
#
# 0 <= roads.length <= min(n × (n - 1) / 2, 2000)
#
# roads[i] = [u_i, v_i, cost_i, tax_i]
#
# 0 <= u_i, v_i <= n - 1
#
# u_i != v_i
#
# 1 <= cost_i <= 10^9
#
# ​​​​​​​1 <= tax_​​​​​​​i <= 100​​​​​​​
#
# There are no repeated edges.
#

# @lc code=start

from typing import List
import heapq


class Solution:
    def minCost(self, n: int, prices: List[int], roads: List[List[int]]) -> List[int]:
        """
        Interview explanation:
        From shop i, either buy locally or travel empty to j, buy there, and
        return loaded. Empty edges cost `cost`; loaded edges cost `cost * tax`.
        Paths may differ, so add independent shortest-path distances.

        Algorithm:
        - Build empty-weight and loaded-weight adjacency lists.
        - For each source i, Dijkstra on both graphs.
        - ans[i] = min_j (d_empty[i][j] + d_loaded[i][j] + prices[j]).

        Complexity: O(n * (n + m) log n) time, O(n + m) space.
        """
        g_empty = [[] for _ in range(n)]
        g_load = [[] for _ in range(n)]
        for u, v, c, t in roads:
            g_empty[u].append((v, c))
            g_empty[v].append((u, c))
            g_load[u].append((v, c * t))
            g_load[v].append((u, c * t))

        def dijkstra(graph, src: int) -> List[int]:
            dist = [10**30] * n
            dist[src] = 0
            pq = [(0, src)]
            while pq:
                d, u = heapq.heappop(pq)
                if d > dist[u]:
                    continue
                for v, w in graph[u]:
                    nd = d + w
                    if nd < dist[v]:
                        dist[v] = nd
                        heapq.heappush(pq, (nd, v))
            return dist

        ans = [0] * n
        for i in range(n):
            de = dijkstra(g_empty, i)
            dl = dijkstra(g_load, i)
            best = prices[i]
            for j in range(n):
                if de[j] < 10**30 and dl[j] < 10**30:
                    best = min(best, de[j] + dl[j] + prices[j])
            ans[i] = best
        return ans
# @lc code=end
