#
# @lc app=leetcode id=834 lang=python3
#
# [834] Sum of Distances in Tree
#
# https://leetcode.com/problems/sum-of-distances-in-tree/description/
#
# algorithms
# Hard (65.72%)
# Likes:    6025
# Dislikes: 140
# Total Accepted:    189K
# Total Submissions: 287K
# Testcase Example:  "6"
#
# There is an undirected connected tree with n nodes labeled from 0 to n - 1
# and n - 1 edges.
#
# You are given the integer n and the array edges where edges[i] = [a_i, b_i]
# indicates that there is an edge between nodes a_i and b_i in the tree.
#
# Return an array answer of length n where answer[i] is the sum of the
# distances between the i^th node in the tree and all other nodes.
#
# Example 1:
#
# Input: n = 6, edges = [[0,1],[0,2],[2,3],[2,4],[2,5]]
# Output: [8,12,6,10,10,10]
# Explanation: The tree is shown above.
# We can see that dist(0,1) + dist(0,2) + dist(0,3) + dist(0,4) + dist(0,5)
# equals 1 + 1 + 2 + 2 + 2 = 8.
# Hence, answer[0] = 8, and so on.
#
# Example 2:
#
# Input: n = 1, edges = []
# Output: [0]
#
# Example 3:
#
# Input: n = 2, edges = [[1,0]]
# Output: [1,1]
#
# Constraints:
#
# 1 <= n <= 3 * 10^4
#
# edges.length == n - 1
#
# edges[i].length == 2
#
# 0 <= a_i, b_i < n
#
# a_i != b_i
#
# The given input represents a valid tree.
#

# @lc code=start

from typing import List
from collections import defaultdict


class Solution:
    def sumOfDistancesInTree(self, n: int, edges: List[List[int]]) -> List[int]:
        """
        Interview explanation:
        Rerooting DP on a tree. First DFS from root 0: compute subtree sizes and
        sum of distances in each subtree. Second DFS reroots: moving root from
        u→v updates ans[v] = ans[u] - size[v] + (n - size[v]).

        Algorithm:
        - Build adjacency list.
        - dfs1(u): size[u], dist_sub[u] = sum distances from u to nodes in subtree.
        - ans[0]=dist_sub[0]; dfs2 reroot formula for children.

        Complexity: O(n) time, O(n) space.
        """
        g = defaultdict(list)
        for a, b in edges:
            g[a].append(b)
            g[b].append(a)
        size = [1] * n
        dist_sub = [0] * n

        def dfs1(u: int, p: int) -> None:
            for v in g[u]:
                if v == p:
                    continue
                dfs1(v, u)
                size[u] += size[v]
                dist_sub[u] += dist_sub[v] + size[v]

        dfs1(0, -1)
        ans = [0] * n
        ans[0] = dist_sub[0]

        def dfs2(u: int, p: int) -> None:
            for v in g[u]:
                if v == p:
                    continue
                ans[v] = ans[u] - size[v] + (n - size[v])
                dfs2(v, u)

        dfs2(0, -1)
        return ans
# @lc code=end
