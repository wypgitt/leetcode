#
# @lc app=leetcode id=3543 lang=python3
#
# [3543] Maximum Weighted K-Edge Path
#
# https://leetcode.com/problems/maximum-weighted-k-edge-path/description/
#
# algorithms
# Medium (20.32%)
# Likes:    93
# Dislikes: 10
# Total Accepted:    10.2K
# Total Submissions: 50.3K
# Testcase Example:  "3\n[[0,1,1],[1,2,2]]\n2\n4"
#
#
# You are given an integer n and a Directed Acyclic Graph (DAG) with n
# nodes labeled from 0 to n - 1. This is represented by a 2D array edges,
# where edges[i] = [u_i, v_i, w_i] indicates a directed edge from node u_i
# to v_i with weight w_i.
#
# You are also given two integers, k and t.
#
# Your task is to determine the maximum possible sum of edge weights for
# any path in the graph such that:
#
# The path contains exactly k edges.
#
# The total sum of edge weights in the path is strictly less than t.
#
# Return the maximum possible sum of weights for such a path. If no such
# path exists, return -1.
#
# Example 1:
#
# Input: n = 3, edges = [[0,1,1],[1,2,2]], k = 2, t = 4
#
# Output: 3
#
# Explanation:
#
# The only path with k = 2 edges is 0 -> 1 -> 2 with weight 1 + 2 = 3 < t.
#
# Thus, the maximum possible sum of weights less than t is 3.
#
# Example 2:
#
# Input: n = 3, edges = [[0,1,2],[0,2,3]], k = 1, t = 3
#
# Output: 2
#
# Explanation:
#
# There are two paths with k = 1 edge:
#
# 0 -> 1 with weight 2 < t.
#
# 0 -> 2 with weight 3 = t, which is not strictly less than t.
#
# Thus, the maximum possible sum of weights less than t is 2.
#
# Example 3:
#
# Input: n = 3, edges = [[0,1,6],[1,2,8]], k = 1, t = 6
#
# Output: -1
#
# Explanation:
#
# There are two paths with k = 1 edge:
#
# 0 -> 1 with weight 6 = t, which is not strictly less than t.
#
# 1 -> 2 with weight 8 > t, which is not strictly less than t.
#
# Since there is no path with sum of weights strictly less than t, the
# answer is -1.
#
# Constraints:
#
# 1 <= n <= 300
#
# 0 <= edges.length <= 300
#
# edges[i] = [u_i, v_i, w_i]
#
# 0 <= u_i, v_i < n
#
# u_i != v_i
#
# 1 <= w_i <= 10
#
# 0 <= k <= 300
#
# 1 <= t <= 600
#
# The input graph is guaranteed to be a DAG.
#
# There are no duplicate edges.
#

# @lc code=start
from typing import List


class Solution:
    def maxWeight(self, n: int, edges: List[List[int]], k: int, t: int) -> int:
        """
        Interview explanation:
        DAG paths with exactly k edges and weight sum strictly < t; maximize
        that sum. Small t and sparse edges make layered DP over reachable sums
        practical.

        Algorithm:
        - dp[e][u] = set of sums of e-edge paths ending at u with sum < t.
        - Initialize dp[0][*] = {0}; relax along outgoing edges for e = 0..k-1.
        - Answer is the max value in any dp[k][u], or -1 if empty.
        - Special case k == 0: empty path sum 0 (always < t).

        Complexity: O(k * (|E| + n) * t) time, O(n * k * t) space.
        """
        if k == 0:
            return 0
        adj: List[List[tuple]] = [[] for _ in range(n)]
        for u, v, w in edges:
            adj[u].append((v, w))

        dp = [[set() for _ in range(n)] for _ in range(k + 1)]
        for u in range(n):
            dp[0][u].add(0)

        for e in range(k):
            for u in range(n):
                if not dp[e][u]:
                    continue
                for s in dp[e][u]:
                    for v, w in adj[u]:
                        ns = s + w
                        if ns < t:
                            dp[e + 1][v].add(ns)

        ans = -1
        for u in range(n):
            if dp[k][u]:
                ans = max(ans, max(dp[k][u]))
        return ans
# @lc code=end
