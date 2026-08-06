#
# @lc app=leetcode id=1697 lang=python3
#
# [1697] Checking Existence of Edge Length Limited Paths
#
# https://leetcode.com/problems/checking-existence-of-edge-length-limited-paths/description/
#
# algorithms
# Hard (63.55%)
# Likes:    2161
# Dislikes: 48
# Total Accepted:    64.2K
# Total Submissions: 101K
# Testcase Example:  "3"
#
# An undirected graph of n nodes is defined by edgeList, where edgeList[i] =
# [u_i, v_i, dis_i] denotes an edge between nodes u_i and v_i with distance
# dis_i. Note that there may be multiple edges between two nodes.
#
# Given an array queries, where queries[j] = [p_j, q_j, limit_j], your task is
# to determine for each queries[j] whether there is a path between p_j and q_j_
# such that each edge on the path has a distance strictly less than limit_j .
#
# Return a boolean array answer, where answer.length == queries.length and the
# j^th value of answer is true if there is a path for queries[j] is true, and
# false otherwise.
#
# Example 1:
#
# Input: n = 3, edgeList = [[0,1,2],[1,2,4],[2,0,8],[1,0,16]], queries =
# [[0,1,2],[0,2,5]]
# Output: [false,true]
# Explanation: The above figure shows the given graph. Note that there are two
# overlapping edges between 0 and 1 with distances 2 and 16.
# For the first query, between 0 and 1 there is no path where each distance is
# less than 2, thus we return false for this query.
# For the second query, there is a path (0 -> 1 -> 2) of two edges with
# distances less than 5, thus we return true for this query.
#
# Example 2:
#
# Input: n = 5, edgeList = [[0,1,10],[1,2,5],[2,3,9],[3,4,13]], queries =
# [[0,4,14],[1,4,13]]
# Output: [true,false]
# Explanation: The above figure shows the given graph.
#
# Constraints:
#
# 2 <= n <= 10^5
#
# 1 <= edgeList.length, queries.length <= 10^5
#
# edgeList[i].length == 3
#
# queries[j].length == 3
#
# 0 <= u_i, v_i, p_j, q_j <= n - 1
#
# u_i != v_i
#
# p_j != q_j
#
# 1 <= dis_i, limit_j <= 10^9
#
# There may be multiple edges between two nodes.
#

# @lc code=start
from typing import List


class Solution:
    def distanceLimitedPathsExist(
        self, n: int, edgeList: List[List[int]], queries: List[List[int]]
    ) -> List[bool]:
        """
        Interview explanation:
        Offline queries: path using only edges with weight < limit? Sort edges
        and queries by weight; Union-Find add edges below limit, then check
        connected.

        Algorithm (Union-Find offline):
        - Sort edges by weight; sort queries by limit with index;
          for each query union edges < limit; ans[i]=connected(p,q).

        Complexity: O((E+Q) α(n) + (E+Q) log) time, O(n+Q) space.
        """
        parent = list(range(n))
        rank = [0] * n

        def find(x):
            while parent[x] != x:
                parent[x] = parent[parent[x]]
                x = parent[x]
            return x

        def union(a, b):
            ra, rb = find(a), find(b)
            if ra == rb:
                return
            if rank[ra] < rank[rb]:
                parent[ra] = rb
            elif rank[ra] > rank[rb]:
                parent[rb] = ra
            else:
                parent[rb] = ra
                rank[ra] += 1

        edges = sorted(edgeList, key=lambda e: e[2])
        qid = sorted(range(len(queries)), key=lambda i: queries[i][2])
        ans = [False] * len(queries)
        ei = 0
        for i in qid:
            p, q, limit = queries[i]
            while ei < len(edges) and edges[ei][2] < limit:
                union(edges[ei][0], edges[ei][1])
                ei += 1
            ans[i] = find(p) == find(q)
        return ans
# @lc code=end
