#
# @lc app=leetcode id=3372 lang=python3
#
# [3372] Maximize the Number of Target Nodes After Connecting Trees I
#
# https://leetcode.com/problems/maximize-the-number-of-target-nodes-after-connecting-trees-i/description/
#
# algorithms
# Medium (69.44%)
# Likes:    448
# Dislikes: 269
# Total Accepted:    85K
# Total Submissions: 122.4K
# Testcase Example:  "[[0,1],[0,2],[2,3],[2,4]]\n[[0,1],[0,2],[0,3],[2,7],[1,4],[4,5],[4,6]]\n2"
#
#
# There exist two undirected trees with n and m nodes, with distinct
# labels in ranges [0, n - 1] and [0, m - 1], respectively.
#
# You are given two 2D integer arrays edges1 and edges2 of lengths n - 1
# and m - 1, respectively, where edges1[i] = [a_i, b_i] indicates that
# there is an edge between nodes a_i and b_i in the first tree and
# edges2[i] = [u_i, v_i] indicates that there is an edge between nodes u_i
# and v_i in the second tree. You are also given an integer k.
#
# Node u is target to node v if the number of edges on the path from u to
# v is less than or equal to k. Note that a node is always target to
# itself.
#
# Return an array of n integers answer, where answer[i] is the maximum
# possible number of nodes target to node i of the first tree if you have
# to connect one node from the first tree to another node in the second
# tree.
#
# Note that queries are independent from each other. That is, for every
# query you will remove the added edge before proceeding to the next
# query.
#
# Example 1:
#
# Input: edges1 = [[0,1],[0,2],[2,3],[2,4]], edges2 =
# [[0,1],[0,2],[0,3],[2,7],[1,4],[4,5],[4,6]], k = 2
#
# Output: [9,7,9,8,8]
#
# Explanation:
#
# For i = 0, connect node 0 from the first tree to node 0 from the second
# tree.
#
# For i = 1, connect node 1 from the first tree to node 0 from the second
# tree.
#
# For i = 2, connect node 2 from the first tree to node 4 from the second
# tree.
#
# For i = 3, connect node 3 from the first tree to node 4 from the second
# tree.
#
# For i = 4, connect node 4 from the first tree to node 4 from the second
# tree.
#
# Example 2:
#
# Input: edges1 = [[0,1],[0,2],[0,3],[0,4]], edges2 = [[0,1],[1,2],[2,3]],
# k = 1
#
# Output: [6,3,3,3,3]
#
# Explanation:
#
# For every i, connect node i of the first tree with any node of the
# second tree.
#
# Constraints:
#
# 2 <= n, m <= 1000
#
# edges1.length == n - 1
#
# edges2.length == m - 1
#
# edges1[i].length == edges2[i].length == 2
#
# edges1[i] = [a_i, b_i]
#
# 0 <= a_i, b_i < n
#
# edges2[i] = [u_i, v_i]
#
# 0 <= u_i, v_i < m
#
# The input is generated such that edges1 and edges2 represent valid
# trees.
#
# 0 <= k <= 1000
#

# @lc code=start
from typing import List


class Solution:
    def maxTargetNodes(
        self, edges1: List[List[int]], edges2: List[List[int]], k: int
    ) -> List[int]:
        """
        Interview explanation:
        Connect i in tree1 to some j in tree2. Targets of i are nodes within k in
        tree1 plus nodes within k-1 of j in tree2. Maximize over j by using the
        best tree2 radius-(k-1) count for every i.

        Algorithm:
        - Build both trees. Precompute max nodes within distance k-1 in tree2.
        - For each i, answer = count_within(i, k) in tree1 + that max.

        Complexity: O(n^2 + m^2) time, O(n + m) space.
        """
        def build(edges: List[List[int]]) -> List[List[int]]:
            n = len(edges) + 1
            g = [[] for _ in range(n)]
            for a, b in edges:
                g[a].append(b)
                g[b].append(a)
            return g

        def dfs(g: List[List[int]], a: int, fa: int, d: int) -> int:
            if d < 0:
                return 0
            cnt = 1
            for b in g[a]:
                if b != fa:
                    cnt += dfs(g, b, a, d - 1)
            return cnt

        g2 = build(edges2)
        m = len(g2)
        t = max(dfs(g2, i, -1, k - 1) for i in range(m))
        g1 = build(edges1)
        n = len(g1)
        return [dfs(g1, i, -1, k) + t for i in range(n)]
# @lc code=end
