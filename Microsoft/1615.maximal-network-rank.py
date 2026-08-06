#
# @lc app=leetcode id=1615 lang=python3
#
# [1615] Maximal Network Rank
#
# https://leetcode.com/problems/maximal-network-rank/description/
#
# algorithms
# Medium (66.06%)
# Likes:    2460
# Dislikes: 394
# Total Accepted:    174K
# Total Submissions: 263K
# Testcase Example:  "4"
#
# There is an infrastructure of n cities with some number of roads connecting
# these cities. Each roads[i] = [a_i, b_i] indicates that there is a
# bidirectional road between cities a_i and b_i.
#
# The network rank of two different cities is defined as the total number of
# directly connected roads to either city. If a road is directly connected to
# both cities, it is only counted once.
#
# The maximal network rank of the infrastructure is the maximum network rank of
# all pairs of different cities.
#
# Given the integer n and the array roads, return the maximal network rank of
# the entire infrastructure.
#
# Example 1:
#
# Input: n = 4, roads = [[0,1],[0,3],[1,2],[1,3]]
# Output: 4
# Explanation: The network rank of cities 0 and 1 is 4 as there are 4 roads
# that are connected to either 0 or 1. The road between 0 and 1 is only counted
# once.
#
# Example 2:
#
# Input: n = 5, roads = [[0,1],[0,3],[1,2],[1,3],[2,3],[2,4]]
# Output: 5
# Explanation: There are 5 roads that are connected to cities 1 or 2.
#
# Example 3:
#
# Input: n = 8, roads = [[0,1],[1,2],[2,3],[2,4],[5,6],[5,7]]
# Output: 5
# Explanation: The network rank of 2 and 5 is 5. Notice that all the cities do
# not have to be connected.
#
# Constraints:
#
# 2 <= n <= 100
#
# 0 <= roads.length <= n * (n - 1) / 2
#
# roads[i].length == 2
#
# 0 <= a_i, b_i <= n-1
#
# a_i != b_i
#
# Each pair of cities has at most one road connecting them.
#

# @lc code=start
from typing import List


class Solution:
    def maximalNetworkRank(self, n: int, roads: List[List[int]]) -> int:
        """
        Interview explanation:
        Network rank of two cities = degree(a)+degree(b) - (1 if edge a-b else 0).
        Check all pairs.

        Algorithm (degrees + edge set):
        - Build degree and undirected edge set; max over all pairs i<j.

        Complexity: O(n^2 + m) time, O(n+m) space.
        """
        deg = [0] * n
        edges = set()
        for a, b in roads:
            deg[a] += 1
            deg[b] += 1
            edges.add((min(a, b), max(a, b)))
        ans = 0
        for i in range(n):
            for j in range(i + 1, n):
                ans = max(ans, deg[i] + deg[j] - ((i, j) in edges))
        return ans

    def maximalNetworkRank_optimized(self, n: int, roads: List[List[int]]) -> int:
        """
        Interview explanation:
        Alternate: sort cities by degree; only need top-degree candidates, but for
        n<=100 full pair scan is fine — here scan focusing higher degrees first.

        Algorithm:
        - Same formula; iterate pairs ordered by deg (still O(n^2)).

        Complexity: O(n^2 + m) time, O(n+m) space.
        """
        g = [set() for _ in range(n)]
        for a, b in roads:
            g[a].add(b)
            g[b].add(a)
        ans = 0
        for i in range(n):
            for j in range(i + 1, n):
                ans = max(ans, len(g[i]) + len(g[j]) - (j in g[i]))
        return ans
# @lc code=end
