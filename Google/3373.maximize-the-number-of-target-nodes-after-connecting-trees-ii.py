#
# @lc app=leetcode id=3373 lang=python3
#
# [3373] Maximize the Number of Target Nodes After Connecting Trees II
#
# https://leetcode.com/problems/maximize-the-number-of-target-nodes-after-connecting-trees-ii/description/
#
# algorithms
# Hard (73.11%)
# Likes:    381
# Dislikes: 44
# Total Accepted:    70.6K
# Total Submissions: 96.5K
# Testcase Example:  "[[0,1],[0,2],[2,3],[2,4]]\n[[0,1],[0,2],[0,3],[2,7],[1,4],[4,5],[4,6]]"
#
#
# There exist two undirected trees with n and m nodes, labeled from [0, n
# - 1] and [0, m - 1], respectively.
#
# You are given two 2D integer arrays edges1 and edges2 of lengths n - 1
# and m - 1, respectively, where edges1[i] = [a_i, b_i] indicates that
# there is an edge between nodes a_i and b_i in the first tree and
# edges2[i] = [u_i, v_i] indicates that there is an edge between nodes u_i
# and v_i in the second tree.
#
# Node u is target to node v if the number of edges on the path from u to
# v is even. Note that a node is always target to itself.
#
# Return an array of n integers answer, where answer[i] is the maximum
# possible number of nodes that are target to node i of the first tree if
# you had to connect one node from the first tree to another node in the
# second tree.
#
# Note that queries are independent from each other. That is, for every
# query you will remove the added edge before proceeding to the next
# query.
#
# Example 1:
#
# Input: edges1 = [[0,1],[0,2],[2,3],[2,4]], edges2 =
# [[0,1],[0,2],[0,3],[2,7],[1,4],[4,5],[4,6]]
#
# Output: [8,7,7,8,8]
#
# Explanation:
#
# For i = 0, connect node 0 from the first tree to node 0 from the second
# tree.
#
# For i = 1, connect node 1 from the first tree to node 4 from the second
# tree.
#
# For i = 2, connect node 2 from the first tree to node 7 from the second
# tree.
#
# For i = 3, connect node 3 from the first tree to node 0 from the second
# tree.
#
# For i = 4, connect node 4 from the first tree to node 4 from the second
# tree.
#
# Example 2:
#
# Input: edges1 = [[0,1],[0,2],[0,3],[0,4]], edges2 = [[0,1],[1,2],[2,3]]
#
# Output: [3,6,6,6,6]
#
# Explanation:
#
# For every i, connect node i of the first tree with any node of the
# second tree.
#
# Constraints:
#
# 2 <= n, m <= 10^5
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

# @lc code=start
from typing import List


class Solution:
    def maxTargetNodes(
        self, edges1: List[List[int]], edges2: List[List[int]]
    ) -> List[int]:
        """
        Interview explanation:
        Target means even distance. Trees are bipartite by parity; connecting an
        edge flips parity into tree2. For node i, keep its even-parity set in
        tree1 and add the larger color class of tree2.

        Algorithm:
        - 2-color both trees; count color sizes.
        - answer[i] = cnt1[color[i]] + max(cnt2).

        Complexity: O(n + m) time, O(n + m) space.
        """
        def build(edges: List[List[int]]) -> List[List[int]]:
            n = len(edges) + 1
            g = [[] for _ in range(n)]
            for a, b in edges:
                g[a].append(b)
                g[b].append(a)
            return g

        def color(g: List[List[int]]) -> tuple[List[int], List[int]]:
            n = len(g)
            c = [0] * n
            cnt = [0, 0]

            def dfs(a: int, fa: int, d: int) -> None:
                c[a] = d
                cnt[d] += 1
                for b in g[a]:
                    if b != fa:
                        dfs(b, a, d ^ 1)

            dfs(0, -1, 0)
            return c, cnt

        g1, g2 = build(edges1), build(edges2)
        c1, cnt1 = color(g1)
        _, cnt2 = color(g2)
        t = max(cnt2)
        return [t + cnt1[c1[i]] for i in range(len(g1))]
# @lc code=end
