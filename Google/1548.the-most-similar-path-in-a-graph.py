#
# @lc app=leetcode id=1548 lang=python3
#
# [1548] The Most Similar Path in a Graph
#
# https://leetcode.com/problems/the-most-similar-path-in-a-graph/description/
#
# algorithms
# Hard (59.46%)
# Likes:    380
# Dislikes: 187
# Total Accepted:    18K
# Total Submissions: 30.2K
# Testcase Example:  "5\n[[0,2],[0,3],[1,2],[1,3],[1,4],[2,4]]\n[\"ATL\",\"PEK\",\"LAX\",\"DXB\",\"HND\"]\n[\"ATL\",\"DXB\",\"HND\",\"LAX\"]"
#
#
# We have n cities and m bi-directional roads where roads[i] = [a_i, b_i]
# connects city a_i with city b_i. Each city has a name consisting of
# exactly three upper-case English letters given in the string array
# names. Starting at any city x, you can reach any city y where y != x
# (i.e., the cities and the roads are forming an undirected connected
# graph).
#
# You will be given a string array targetPath. You should find a path in
# the graph of the same length and with the minimum edit distance to
# targetPath.
#
# You need to return the order of the nodes in the path with the minimum
# edit distance. The path should be of the same length of targetPath and
# should be valid (i.e., there should be a direct road between ans[i] and
# ans[i + 1]). If there are multiple answers return any one of them.
#
# The edit distance is defined as follows:
#
# Example 1:
#
# Input: n = 5, roads = [[0,2],[0,3],[1,2],[1,3],[1,4],[2,4]], names =
# ["ATL","PEK","LAX","DXB","HND"], targetPath = ["ATL","DXB","HND","LAX"]
# Output: [0,2,4,2]
# Explanation: [0,2,4,2], [0,3,0,2] and [0,3,1,2] are accepted answers.
# [0,2,4,2] is equivalent to ["ATL","LAX","HND","LAX"] which has edit
# distance = 1 with targetPath.
# [0,3,0,2] is equivalent to ["ATL","DXB","ATL","LAX"] which has edit
# distance = 1 with targetPath.
# [0,3,1,2] is equivalent to ["ATL","DXB","PEK","LAX"] which has edit
# distance = 1 with targetPath.
#
# Example 2:
#
# Input: n = 4, roads = [[1,0],[2,0],[3,0],[2,1],[3,1],[3,2]], names =
# ["ATL","PEK","LAX","DXB"], targetPath =
# ["ABC","DEF","GHI","JKL","MNO","PQR","STU","VWX"]
# Output: [0,1,0,1,0,1,0,1]
# Explanation: Any path in this graph has edit distance = 8 with
# targetPath.
#
# Example 3:
#
# Input: n = 6, roads = [[0,1],[1,2],[2,3],[3,4],[4,5]], names =
# ["ATL","PEK","LAX","ATL","DXB","HND"], targetPath =
# ["ATL","DXB","HND","DXB","ATL","LAX","PEK"]
# Output: [3,4,5,4,3,2,1]
# Explanation: [3,4,5,4,3,2,1] is the only path with edit distance = 0
# with targetPath.
# It's equivalent to ["ATL","DXB","HND","DXB","ATL","LAX","PEK"]
#
# Constraints:
#
# 2 <= n <= 100
#
# m == roads.length
#
# n - 1 <= m <= (n * (n - 1) / 2)
#
# 0 <= a_i, b_i <= n - 1
#
# a_i != b_i
#
# The graph is guaranteed to be connected and each pair of nodes may have
# at most one direct road.
#
# names.length == n
#
# names[i].length == 3
#
# names[i] consists of upper-case English letters.
#
# There can be two cities with the same name.
#
# 1 <= targetPath.length <= 100
#
# targetPath[i].length == 3
#
# targetPath[i] consists of upper-case English letters.
#
# Follow up: If each node can be visited only once in the path, What
# should you change in your solution?
#
# @lc code=start
from typing import List
from collections import defaultdict


class Solution:
    def mostSimilar(
        self, n: int, roads: List[List[int]], names: List[str], targetPath: List[str]
    ) -> List[int]:
        """
        Interview explanation:
        Premium. Find a path (adjacent via roads) of length = len(targetPath)
        minimizing edit distance (#positions where names[path[i]]!=targetPath[i]).
        DP: dp[i][u]=min cost using path of length i ending at u; prev for path.

        Algorithm:
        - Build adj; dp[0][u]=(names[u]!=target[0]); transition u→v:
          dp[i][v]=min(dp[i-1][u]+(names[v]!=target[i])); reconstruct path.

        Complexity: O(m * |target| * deg) ~ O(|target| * n^2) time, O(|target|*n) space.
        """
        g = defaultdict(list)
        for a, b in roads:
            g[a].append(b)
            g[b].append(a)
        m = len(targetPath)
        INF = 10**9
        dp = [[INF] * n for _ in range(m)]
        prev = [[-1] * n for _ in range(m)]
        for u in range(n):
            dp[0][u] = 0 if names[u] == targetPath[0] else 1
        for i in range(1, m):
            for u in range(n):
                if dp[i - 1][u] >= INF:
                    continue
                for v in g[u]:
                    cost = dp[i - 1][u] + (0 if names[v] == targetPath[i] else 1)
                    if cost < dp[i][v]:
                        dp[i][v] = cost
                        prev[i][v] = u
        end = min(range(n), key=lambda u: dp[m - 1][u])
        path = [0] * m
        path[m - 1] = end
        for i in range(m - 1, 0, -1):
            path[i - 1] = prev[i][path[i]]
        return path
# @lc code=end
