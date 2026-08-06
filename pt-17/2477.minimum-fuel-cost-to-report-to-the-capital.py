#
# @lc app=leetcode id=2477 lang=python3
#
# [2477] Minimum Fuel Cost to Report to the Capital
#
# https://leetcode.com/problems/minimum-fuel-cost-to-report-to-the-capital/description/
#
# algorithms
# Medium (65.36%)
# Likes:    2341
# Dislikes: 99
# Total Accepted:    92.6K
# Total Submissions: 141.6K
# Testcase Example:  "[[0,1],[0,2],[0,3]]\n5"
#
# There is a tree (i.e., a connected, undirected graph with no cycles) structure
# country network consisting of n cities numbered from 0 to n - 1 and exactly n
# - 1 roads. The capital city is city 0. You are given a 2D integer array roads
# where roads[i] = [a_i, b_i] denotes that there exists a bidirectional road
# connecting cities a_i and b_i.
#
# There is a meeting for the representatives of each city. The meeting is in the
# capital city.
#
# There is a car in each city. You are given an integer seats that indicates the
# number of seats in each car.
#
# A representative can use the car in their city to travel or change the car and
# ride with another representative. The cost of traveling between two cities is
# one liter of fuel.
#
# Return the minimum number of liters of fuel to reach the capital city.
#
#
#
# Example 1:
#
# Input: roads = [[0,1],[0,2],[0,3]], seats = 5
# Output: 3
# Explanation:
# - Representative_1 goes directly to the capital with 1 liter of fuel.
# - Representative_2 goes directly to the capital with 1 liter of fuel.
# - Representative_3 goes directly to the capital with 1 liter of fuel.
# It costs 3 liters of fuel at minimum.
# It can be proven that 3 is the minimum number of liters of fuel needed.
#
# Example 2:
#
# Input: roads = [[3,1],[3,2],[1,0],[0,4],[0,5],[4,6]], seats = 2
# Output: 7
# Explanation:
# - Representative_2 goes directly to city 3 with 1 liter of fuel.
# - Representative_2 and representative_3 go together to city 1 with 1 liter of
# fuel.
# - Representative_2 and representative_3 go together to the capital with 1
# liter of fuel.
# - Representative_1 goes directly to the capital with 1 liter of fuel.
# - Representative_5 goes directly to the capital with 1 liter of fuel.
# - Representative_6 goes directly to city 4 with 1 liter of fuel.
# - Representative_4 and representative_6 go together to the capital with 1
# liter of fuel.
# It costs 7 liters of fuel at minimum.
# It can be proven that 7 is the minimum number of liters of fuel needed.
#
# Example 3:
#
# Input: roads = [], seats = 1
# Output: 0
# Explanation: No representatives need to travel to the capital city.
#
#
#
# Constraints:
#
#
# 1 <= n <= 10^5
#
#
# roads.length == n - 1
#
#
# roads[i].length == 2
#
#
# 0 <= a_i, b_i < n
#
#
# a_i != b_i
#
#
# roads represents a valid tree.
#
#
# 1 <= seats <= 10^5
#

# @lc code=start
from typing import List
from collections import defaultdict
from math import ceil


class Solution:
    def minimumFuelCost(self, roads: List[List[int]], seats: int) -> int:
        """
        Interview explanation:
        Tree rooted at 0; every node has one rep who must reach capital.
        Cars carry up to `seats`; fuel = edges traversed by cars. Minimize fuel.

        Algorithm:
        - DFS subtree sizes; each edge to parent needs ceil(size/seats) cars.

        Complexity: O(n) time, O(n) space.
        """
        g = defaultdict(list)
        for a, b in roads:
            g[a].append(b)
            g[b].append(a)
        ans = 0

        def dfs(u: int, p: int) -> int:
            nonlocal ans
            size = 1
            for v in g[u]:
                if v != p:
                    size += dfs(v, u)
            if u != 0:
                ans += ceil(size / seats)
            return size

        dfs(0, -1)
        return ans
# @lc code=end

