#
# @lc app=leetcode id=1473 lang=python3
#
# [1473] Paint House III
#
# https://leetcode.com/problems/paint-house-iii/description/
#
# algorithms
# Hard (61.26%)
# Likes:    2144
# Dislikes: 157
# Total Accepted:    74.2K
# Total Submissions: 121K
# Testcase Example:  "[0,0,0,0,0]"
#
# There is a row of m houses in a small city, each house must be painted with
# one of the n colors (labeled from 1 to n), some houses that have been painted
# last summer should not be painted again.
#
# A neighborhood is a maximal group of continuous houses that are painted with
# the same color.
#
# For example: houses = [1,2,2,3,3,2,1,1] contains 5 neighborhoods [{1}, {2,2},
# {3,3}, {2}, {1,1}].
#
# Given an array houses, an m x n matrix cost and an integer target where:
#
# houses[i]: is the color of the house i, and 0 if the house is not painted
# yet.
#
# cost[i][j]: is the cost of paint the house i with the color j + 1.
#
# Return the minimum cost of painting all the remaining houses in such a way
# that there are exactly target neighborhoods. If it is not possible, return
# -1.
#
# Example 1:
#
# Input: houses = [0,0,0,0,0], cost = [[1,10],[10,1],[10,1],[1,10],[5,1]], m =
# 5, n = 2, target = 3
# Output: 9
# Explanation: Paint houses of this way [1,2,2,1,1]
# This array contains target = 3 neighborhoods, [{1}, {2,2}, {1,1}].
# Cost of paint all houses (1 + 1 + 1 + 1 + 5) = 9.
#
# Example 2:
#
# Input: houses = [0,2,1,2,0], cost = [[1,10],[10,1],[10,1],[1,10],[5,1]], m =
# 5, n = 2, target = 3
# Output: 11
# Explanation: Some houses are already painted, Paint the houses of this way
# [2,2,1,2,2]
# This array contains target = 3 neighborhoods, [{2,2}, {1}, {2,2}].
# Cost of paint the first and last house (10 + 1) = 11.
#
# Example 3:
#
# Input: houses = [3,1,2,3], cost = [[1,1,1],[1,1,1],[1,1,1],[1,1,1]], m = 4, n
# = 3, target = 3
# Output: -1
# Explanation: Houses are already painted with a total of 4 neighborhoods
# [{3},{1},{2},{3}] different of target = 3.
#
# Constraints:
#
# m == houses.length == cost.length
#
# n == cost[i].length
#
# 1 <= m <= 100
#
# 1 <= n <= 20
#
# 1 <= target <= m
#
# 0 <= houses[i] <= n
#
# 1 <= cost[i][j] <= 10^4
#

# @lc code=start
from typing import List
from functools import lru_cache


class Solution:
    def minCost(
        self, houses: List[int], cost: List[List[int]], m: int, n: int, target: int
    ) -> int:
        """
        Interview explanation:
        Paint houses with at most n colors forming exactly target neighborhoods
        (contiguous same color). Some houses pre-painted (houses[i]>0). DP on
        (index, neighborhoods_so_far, prev_color).

        Algorithm:
        - dfs(i, neigh, prev): if i==m return 0 if neigh==target else inf.
          If painted, recurse with updated neigh; else try all colors + cost.

        Complexity: O(m * target * n^2) time/space.
        """
        INF = 10**15

        @lru_cache(None)
        def dp(i, neigh, prev):
            if neigh > target:
                return INF
            if i == m:
                return 0 if neigh == target else INF
            ans = INF
            if houses[i]:
                c = houses[i]
                ans = dp(i + 1, neigh + (c != prev), c)
            else:
                for c in range(1, n + 1):
                    ans = min(ans, cost[i][c - 1] + dp(i + 1, neigh + (c != prev), c))
            return ans

        res = dp(0, 0, 0)
        return -1 if res >= INF else res

    def minCost_bottomup(
        self, houses: List[int], cost: List[List[int]], m: int, n: int, target: int
    ) -> int:
        """
        Interview explanation:
        Alternate: iterative DP dp[i][neigh][color] = min cost painting first i
        houses with `neigh` neighborhoods ending in `color`.

        Algorithm:
        - Initialize for house 0; transition i-1→i updating neighborhood count
          when color changes; answer min over colors at neigh==target.

        Complexity: O(m * target * n^2) time/space.
        """
        INF = 10**15
        # dp[neigh][color] after processing current house (1-index colors)
        dp = [[INF] * (n + 1) for _ in range(target + 1)]
        if houses[0]:
            dp[1][houses[0]] = 0
        else:
            for c in range(1, n + 1):
                dp[1][c] = cost[0][c - 1]
        for i in range(1, m):
            ndp = [[INF] * (n + 1) for _ in range(target + 1)]
            colors = range(houses[i], houses[i] + 1) if houses[i] else range(1, n + 1)
            for neigh in range(1, target + 1):
                for prev in range(1, n + 1):
                    if dp[neigh][prev] >= INF:
                        continue
                    for c in colors:
                        nn = neigh + (c != prev)
                        if nn > target:
                            continue
                        add = 0 if houses[i] else cost[i][c - 1]
                        ndp[nn][c] = min(ndp[nn][c], dp[neigh][prev] + add)
            dp = ndp
        ans = min(dp[target][1:])
        return -1 if ans >= INF else ans

# @lc code=end
