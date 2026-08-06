#
# @lc app=leetcode id=3419 lang=python3
#
# [3419] Minimize the Maximum Edge Weight of Graph
#
# https://leetcode.com/problems/minimize-the-maximum-edge-weight-of-graph/description/
#
# algorithms
# Medium (45.41%)
# Likes:    260
# Dislikes: 20
# Total Accepted:    17K
# Total Submissions: 37.4K
# Testcase Example:  "5\n[[1,0,1],[2,0,2],[3,0,1],[4,3,1],[2,1,1]]\n2"
#
#
# You are given two integers, n and threshold, as well as a directed
# weighted graph of n nodes numbered from 0 to n - 1. The graph is
# represented by a 2D integer array edges, where edges[i] = [A_i, B_i,
# W_i] indicates that there is an edge going from node A_i to node B_i
# with weight W_i.
#
# You have to remove some edges from this graph (possibly none), so that
# it satisfies the following conditions:
#
# Node 0 must be reachable from all other nodes.
#
# The maximum edge weight in the resulting graph is minimized.
#
# Each node has at most threshold outgoing edges.
#
# Return the minimum possible value of the maximum edge weight after
# removing the necessary edges. If it is impossible for all conditions to
# be satisfied, return -1.
#
# Example 1:
#
# Input: n = 5, edges = [[1,0,1],[2,0,2],[3,0,1],[4,3,1],[2,1,1]],
# threshold = 2
#
# Output: 1
#
# Explanation:
#
# Remove the edge 2 -> 0. The maximum weight among the remaining edges is
# 1.
#
# Example 2:
#
# Input: n = 5, edges = [[0,1,1],[0,2,2],[0,3,1],[0,4,1],[1,2,1],[1,4,1]],
# threshold = 1
#
# Output: -1
#
# Explanation:
#
# It is impossible to reach node 0 from node 2.
#
# Example 3:
#
# Input: n = 5, edges = [[1,2,1],[1,3,3],[1,4,5],[2,3,2],[3,4,2],[4,0,1]],
# threshold = 1
#
# Output: 2
#
# Explanation:
#
# Remove the edges 1 -> 3 and 1 -> 4. The maximum weight among the
# remaining edges is 2.
#
# Example 4:
#
# Input: n = 5, edges = [[1,2,1],[1,3,3],[1,4,5],[2,3,2],[4,0,1]],
# threshold = 1
#
# Output: -1
#
# Constraints:
#
# 2 <= n <= 10^5
#
# 1 <= threshold <= n - 1
#
# 1 <= edges.length <= min(10^5, n * (n - 1) / 2).
#
# edges[i].length == 3
#
# 0 <= A_i, B_i < n
#
# A_i != B_i
#
# 1 <= W_i <= 10^6
#
# There may be multiple edges between a pair of nodes, but they must have
# unique weights.
#

# @lc code=start
from collections import deque
from typing import List


class Solution:
    def minMaxWeight(self, n: int, edges: List[List[int]], threshold: int) -> int:
        """
        Interview explanation:
        Keep a subgraph where 0 is reachable from every node, each node has
        <= threshold out-edges, and the max kept edge weight is minimized.
        Since threshold >= 1, a functional path into 0 uses one out-edge per
        node, so threshold never binds; binary-search the max weight and
        check reverse-reachability from 0.

        Algorithm:
        - Build reverse adjacency lists.
        - Binary search W; BFS/DFS from 0 on reverse edges with weight <= W.
        - Feasible iff all n nodes are reached.

        Complexity: O((n+m) log W) time, O(n+m) space.
        """
        rev = [[] for _ in range(n)]
        max_w = 0
        for u, v, w in edges:
            rev[v].append((u, w))
            max_w = max(max_w, w)

        def reachable(limit: int) -> bool:
            seen = [False] * n
            seen[0] = True
            q = deque([0])
            cnt = 1
            while q:
                u = q.popleft()
                for v, w in rev[u]:
                    if w <= limit and not seen[v]:
                        seen[v] = True
                        cnt += 1
                        q.append(v)
            return cnt == n

        lo, hi = 1, max_w + 1
        ans = -1
        while lo < hi:
            mid = (lo + hi) // 2
            if reachable(mid):
                ans = mid
                hi = mid
            else:
                lo = mid + 1
        return ans
# @lc code=end
