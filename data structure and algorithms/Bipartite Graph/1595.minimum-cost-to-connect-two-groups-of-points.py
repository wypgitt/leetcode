#
# @lc app=leetcode id=1595 lang=python3
#
# [1595] Minimum Cost to Connect Two Groups of Points
#
# https://leetcode.com/problems/minimum-cost-to-connect-two-groups-of-points/description/
#
# algorithms
# Hard (50.45%)
# Likes:    500
# Dislikes: 16
# Total Accepted:    12.9K
# Total Submissions: 25.6K
# Testcase Example:  "[[15,96],[36,2]]"
#
# You are given two groups of points where the first group has size_1 points,
# the second group has size_2 points, and size_1 >= size_2.
#
# The cost of the connection between any two points are given in an size_1 x
# size_2 matrix where cost[i][j] is the cost of connecting point i of the first
# group and point j of the second group. The groups are connected if each point
# in both groups is connected to one or more points in the opposite group. In
# other words, each point in the first group must be connected to at least one
# point in the second group, and each point in the second group must be
# connected to at least one point in the first group.
#
# Return the minimum cost it takes to connect the two groups.
#
# Example 1:
#
# Input: cost = [[15, 96], [36, 2]]
# Output: 17
# Explanation: The optimal way of connecting the groups is:
# 1--A
# 2--B
# This results in a total cost of 17.
#
# Example 2:
#
# Input: cost = [[1, 3, 5], [4, 1, 1], [1, 5, 3]]
# Output: 4
# Explanation: The optimal way of connecting the groups is:
# 1--A
# 2--B
# 2--C
# 3--A
# This results in a total cost of 4.
# Note that there are multiple points connected to point 2 in the first group
# and point A in the second group. This does not matter as there is no limit to
# the number of points that can be connected. We only care about the minimum
# total cost.
#
# Example 3:
#
# Input: cost = [[2, 5, 1], [3, 4, 7], [8, 1, 2], [6, 2, 4], [3, 8, 8]]
# Output: 10
#
# Constraints:
#
# size_1 == cost.length
#
# size_2 == cost[i].length
#
# 1 <= size_1, size_2 <= 12
#
# size_1 >= size_2
#
# 0 <= cost[i][j] <= 100
#

# @lc code=start
from typing import List
from functools import lru_cache


class Solution:
    def connectTwoGroups(self, cost: List[List[int]]) -> int:
        """
        Interview explanation:
        Bipartite: connect every point in group1 and group2; edge cost given.
        Each point needs ≥1 edge. DP over group1 index + bitmask of covered
        group2: assign edges for current left point to any nonempty subset of
        right, or connect uncovered right at the end via cheapest left edges.

        Algorithm (DP bitmask):
        - m=#left, n=#right; min_right[j]=min cost to connect right j to any left.
        - dp(i, mask): process left i..; mask = connected rights.
        - At i==m: add min_right[j] for unset bits.
        - Else: try connect i to each j (update mask/cost) — actually must try
          all subsets; optimized: for each j connect i-j then recurse, and also
          ensure later; standard solution: for each left, try each right edge
          then at end fix uncovered.

        Classic optimal:
        - dp[i][mask] after considering first i left points.
        - Transition: for current left i, for each right j, dp[i+1][mask|1<<j]
          = cost[i][j] + dp[i][mask].
        - After all left: for unset j add min over left of cost[*][j].

        Complexity: O(m * 2^n * n) time, O(m * 2^n) space (n<=12).
        """
        m, n = len(cost), len(cost[0])
        min_r = [min(cost[i][j] for i in range(m)) for j in range(n)]

        @lru_cache(None)
        def dp(i: int, mask: int) -> int:
            if i == m:
                ans = 0
                for j in range(n):
                    if (mask >> j) & 1 == 0:
                        ans += min_r[j]
                return ans
            ans = 10**18
            for j in range(n):
                ans = min(ans, cost[i][j] + dp(i + 1, mask | (1 << j)))
            return ans

        return dp(0, 0)
# @lc code=end

