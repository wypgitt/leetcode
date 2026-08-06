#
# @lc app=leetcode id=2959 lang=python3
#
# [2959] Number of Possible Sets of Closing Branches
#
# https://leetcode.com/problems/number-of-possible-sets-of-closing-branches/description/
#
# algorithms
# Hard (50.60%)
# Likes:    214
# Dislikes: 17
# Total Accepted:    11.7K
# Total Submissions: 23.2K
# Testcase Example:  "3\n5\n[[0,1,2],[1,2,10],[0,2,10]]"
#
#
# There is a company with n branches across the country, some of which are
# connected by roads. Initially, all branches are reachable from each
# other by traveling some roads.
#
# The company has realized that they are spending an excessive amount of
# time traveling between their branches. As a result, they have decided to
# close down some of these branches (possibly none). However, they want to
# ensure that the remaining branches have a distance of at most
# maxDistance from each other.
#
# The distance between two branches is the minimum total traveled length
# needed to reach one branch from another.
#
# You are given integers n, maxDistance, and a 0-indexed 2D array roads,
# where roads[i] = [u_i, v_i, w_i] represents the undirected road between
# branches u_i and v_i with length w_i.
#
# Return the number of possible sets of closing branches, so that any
# branch has a distance of at most maxDistance from any other.
#
# Note that, after closing a branch, the company will no longer have
# access to any roads connected to it.
#
# Note that, multiple roads are allowed.
#
# Example 1:
#
# Input: n = 3, maxDistance = 5, roads = [[0,1,2],[1,2,10],[0,2,10]]
# Output: 5
# Explanation: The possible sets of closing branches are:
# - The set [2], after closing, active branches are [0,1] and they are
# reachable to each other within distance 2.
# - The set [0,1], after closing, the active branch is [2].
# - The set [1,2], after closing, the active branch is [0].
# - The set [0,2], after closing, the active branch is [1].
# - The set [0,1,2], after closing, there are no active branches.
# It can be proven, that there are only 5 possible sets of closing
# branches.
#
# Example 2:
#
# Input: n = 3, maxDistance = 5, roads =
# [[0,1,20],[0,1,10],[1,2,2],[0,2,2]]
# Output: 7
# Explanation: The possible sets of closing branches are:
# - The set [], after closing, active branches are [0,1,2] and they are
# reachable to each other within distance 4.
# - The set [0], after closing, active branches are [1,2] and they are
# reachable to each other within distance 2.
# - The set [1], after closing, active branches are [0,2] and they are
# reachable to each other within distance 2.
# - The set [0,1], after closing, the active branch is [2].
# - The set [1,2], after closing, the active branch is [0].
# - The set [0,2], after closing, the active branch is [1].
# - The set [0,1,2], after closing, there are no active branches.
# It can be proven, that there are only 7 possible sets of closing
# branches.
#
# Example 3:
#
# Input: n = 1, maxDistance = 10, roads = []
# Output: 2
# Explanation: The possible sets of closing branches are:
# - The set [], after closing, the active branch is [0].
# - The set [0], after closing, there are no active branches.
# It can be proven, that there are only 2 possible sets of closing
# branches.
#
# Constraints:
#
# 1 <= n <= 10
#
# 1 <= maxDistance <= 10^5
#
# 0 <= roads.length <= 1000
#
# roads[i].length == 3
#
# 0 <= u_i, v_i <= n - 1
#
# u_i != v_i
#
# 1 <= w_i <= 1000
#
# All branches are reachable from each other by traveling some roads.
#

# @lc code=start
from typing import List


class Solution:
    def numberOfSets(self, n: int, maxDistance: int, roads: List[List[int]]) -> int:
        """
        Interview explanation:
        Close any subset of branches; remaining pairwise shortest paths must
        be <= maxDistance. n <= 10 => enumerate subsets.

        Algorithm:
        - For each bitmask of open nodes, Floyd-Warshall on induced edges
          (min weight per pair); verify all open pairs within maxDistance.
        - Empty open set always valid.

        Complexity: O(2^n * n^3 + 2^n * |roads|) time, O(n^2) space.
        """
        INF = 10**9
        ans = 0
        for mask in range(1 << n):
            dist = [[INF] * n for _ in range(n)]
            for i in range(n):
                if mask >> i & 1:
                    dist[i][i] = 0
            for u, v, w in roads:
                if (mask >> u & 1) and (mask >> v & 1):
                    if w < dist[u][v]:
                        dist[u][v] = dist[v][u] = w
            for k in range(n):
                if not (mask >> k & 1):
                    continue
                for i in range(n):
                    if not (mask >> i & 1):
                        continue
                    dik = dist[i][k]
                    if dik >= INF:
                        continue
                    for j in range(n):
                        if mask >> j & 1:
                            cand = dik + dist[k][j]
                            if cand < dist[i][j]:
                                dist[i][j] = cand
            ok = True
            nodes = [i for i in range(n) if mask >> i & 1]
            for a in range(len(nodes)):
                for b in range(a + 1, len(nodes)):
                    if dist[nodes[a]][nodes[b]] > maxDistance:
                        ok = False
                        break
                if not ok:
                    break
            if ok:
                ans += 1
        return ans
# @lc code=end

