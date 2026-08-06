#
# @lc app=leetcode id=1719 lang=python3
#
# [1719] Number Of Ways To Reconstruct A Tree
#
# https://leetcode.com/problems/number-of-ways-to-reconstruct-a-tree/description/
#
# algorithms
# Hard (46.12%)
# Likes:    240
# Dislikes: 160
# Total Accepted:    7.3K
# Total Submissions: 15.9K
# Testcase Example:  "[[1,2],[2,3]]"
#
# You are given an array pairs, where pairs[i] = [x_i, y_i], and:
#
# There are no duplicates.
#
# x_i < y_i
#
# Let ways be the number of rooted trees that satisfy the following conditions:
#
# The tree consists of nodes whose values appeared in pairs.
#
# A pair [x_i, y_i] exists in pairs if and only if x_i is an ancestor of y_i or
# y_i is an ancestor of x_i.
#
# Note: the tree does not have to be a binary tree.
#
# Two ways are considered to be different if there is at least one node that
# has different parents in both ways.
#
# Return:
#
# 0 if ways == 0
#
# 1 if ways == 1
#
# 2 if ways > 1
#
# A rooted tree is a tree that has a single root node, and all edges are
# oriented to be outgoing from the root.
#
# An ancestor of a node is any node on the path from the root to that node
# (excluding the node itself). The root has no ancestors.
#
# Example 1:
#
# Input: pairs = [[1,2],[2,3]]
# Output: 1
# Explanation: There is exactly one valid rooted tree, which is shown in the
# above figure.
#
# Example 2:
#
# Input: pairs = [[1,2],[2,3],[1,3]]
# Output: 2
# Explanation: There are multiple valid rooted trees. Three of them are shown
# in the above figures.
#
# Example 3:
#
# Input: pairs = [[1,2],[2,3],[2,4],[1,5]]
# Output: 0
# Explanation: There are no valid rooted trees.
#
# Constraints:
#
# 1 <= pairs.length <= 10^5
#
# 1 <= x_i < y_i <= 500
#
# The elements in pairs are unique.
#

# @lc code=start
from typing import List
from collections import defaultdict


class Solution:
    def checkWays(self, pairs: List[List[int]]) -> int:
        """
        Interview explanation:
        pairs lists ancestor-descendant (undirected) edges of some rooted tree.
        Reconstruct: degree in the "pair graph" equals subtree sizes; the node
        adjacent to all others is the root. Greedy assign parents by sorted degree;
        detect if multiple roots possible (return 2) or unique (1) or impossible (0).

        Algorithm:
        - Build adjacency sets from pairs.
        - Sort nodes by degree descending; root = highest degree (must connect to all).
        - For each next node, find parent = smallest-degree neighbor already placed
          that contains all of node's neighbors; validate ancestor sets.
        - Track whether any node had ≥2 candidate parents → 2 else 1; fail → 0.

        Complexity: O(n^2) typical for constraints, O(n+|pairs|) space.
        """
        g = defaultdict(set)
        for u, v in pairs:
            g[u].add(v)
            g[v].add(u)
        nodes = sorted(g.keys(), key=lambda x: len(g[x]), reverse=True)
        n = len(nodes)
        if len(g[nodes[0]]) != n - 1:
            return 0
        # parent candidates
        ways = 1
        parent = {}
        for i, x in enumerate(nodes):
            if i == 0:
                parent[x] = None
                continue
            # candidates among neighbors already considered with degree >= deg(x)
            cand = None
            for y in g[x]:
                if y in parent and (cand is None or len(g[y]) < len(g[cand])):
                    cand = y
            if cand is None:
                return 0
            # g[x] must be subset of g[cand] ∪ {cand}
            if not g[x].issubset(g[cand] | {cand}):
                return 0
            if len(g[x]) == len(g[cand]):
                ways = 2
            parent[x] = cand
        return ways
# @lc code=end
