#
# @lc app=leetcode id=2497 lang=python3
#
# [2497] Maximum Star Sum of a Graph
#
# https://leetcode.com/problems/maximum-star-sum-of-a-graph/description/
#
# algorithms
# Medium (42.64%)
# Likes:    457
# Dislikes: 62
# Total Accepted:    32.9K
# Total Submissions: 77.2K
# Testcase Example:  "[1,2,3,4,10,-10,-20]\n[[0,1],[1,2],[1,3],[3,4],[3,5],[3,6]]\n2"
#
# There is an undirected graph consisting of n nodes numbered from 0 to n - 1.
# You are given a 0-indexed integer array vals of length n where vals[i] denotes
# the value of the i^th node.
#
# You are also given a 2D integer array edges where edges[i] = [a_i, b_i]
# denotes that there exists an undirected edge connecting nodes a_i and b_i.
#
# A star graph is a subgraph of the given graph having a center node containing
# 0 or more neighbors. In other words, it is a subset of edges of the given
# graph such that there exists a common node for all edges.
#
# The image below shows star graphs with 3 and 4 neighbors respectively,
# centered at the blue node.
#
# The star sum is the sum of the values of all the nodes present in the star
# graph.
#
# Given an integer k, return the maximum star sum of a star graph containing at
# most k edges.
#
#
#
# Example 1:
#
# Input: vals = [1,2,3,4,10,-10,-20], edges =
# [[0,1],[1,2],[1,3],[3,4],[3,5],[3,6]], k = 2
# Output: 16
# Explanation: The above diagram represents the input graph.
# The star graph with the maximum star sum is denoted by blue. It is centered at
# 3 and includes its neighbors 1 and 4.
# It can be shown it is not possible to get a star graph with a sum greater than
# 16.
#
# Example 2:
#
# Input: vals = [-5], edges = [], k = 0
# Output: -5
# Explanation: There is only one possible star graph, which is node 0 itself.
# Hence, we return -5.
#
#
#
# Constraints:
#
#
# n == vals.length
#
#
# 1 <= n <= 10^5
#
#
# -10^4 <= vals[i] <= 10^4
#
#
# 0 <= edges.length <= min(n * (n - 1) / 2, 10^5)
#
#
# edges[i].length == 2
#
#
# 0 <= a_i, b_i <= n - 1
#
#
# a_i != b_i
#
#
# 0 <= k <= n - 1
#

# @lc code=start
from typing import List
from collections import defaultdict
import heapq


class Solution:
    def maxStarSum(self, vals: List[int], edges: List[List[int]], k: int) -> int:
        """
        Interview explanation:
        Star = center + up to k neighbors. Max sum of node values in any star
        (neighbors with negative values can be skipped).

        Algorithm:
        - For each node, take up to k largest positive neighbor values + self.

        Complexity: O(n + m log m) time, O(n+m) space.
        """
        g = defaultdict(list)
        for a, b in edges:
            g[a].append(vals[b])
            g[b].append(vals[a])
        ans = max(vals)
        for u, neigh in g.items():
            pos = sorted((x for x in neigh if x > 0), reverse=True)[:k]
            ans = max(ans, vals[u] + sum(pos))
        return ans
# @lc code=end

