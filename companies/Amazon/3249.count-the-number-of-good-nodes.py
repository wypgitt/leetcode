#
# @lc app=leetcode id=3249 lang=python3
#
# [3249] Count the Number of Good Nodes
#
# https://leetcode.com/problems/count-the-number-of-good-nodes/description/
#
# algorithms
# Medium (54.98%)
# Likes:    181
# Dislikes: 51
# Total Accepted:    32K
# Total Submissions: 58.2K
# Testcase Example:  "[[0,1],[0,2],[1,3],[1,4],[2,5],[2,6]]"
#
#
# There is an undirected tree with n nodes labeled from 0 to n - 1, and
# rooted at node 0. You are given a 2D integer array edges of length n -
# 1, where edges[i] = [a_i, b_i] indicates that there is an edge between
# nodes a_i and b_i in the tree.
#
# A node is good if all the subtrees rooted at its children have the same
# size.
#
# Return the number of good nodes in the given tree.
#
# A subtree of treeName is a tree consisting of a node in treeName and all
# of its descendants.
#
# Example 1:
#
# Input: edges = [[0,1],[0,2],[1,3],[1,4],[2,5],[2,6]]
#
# Output: 7
#
# Explanation:
#
# All of the nodes of the given tree are good.
#
# Example 2:
#
# Input: edges = [[0,1],[1,2],[2,3],[3,4],[0,5],[1,6],[2,7],[3,8]]
#
# Output: 6
#
# Explanation:
#
# There are 6 good nodes in the given tree. They are colored in the image
# above.
#
# Example 3:
#
# Input: edges =
# [[0,1],[1,2],[1,3],[1,4],[0,5],[5,6],[6,7],[7,8],[0,9],[9,10],[9,12],[10,11]]
#
# Output: 12
#
# Explanation:
#
# All nodes except node 9 are good.
#
# Constraints:
#
# 2 <= n <= 10^5
#
# edges.length == n - 1
#
# edges[i].length == 2
#
# 0 <= a_i, b_i < n
#
# The input is generated such that edges represents a valid tree.
#

# @lc code=start
from typing import List


class Solution:
    def countGoodNodes(self, edges: List[List[int]]) -> int:
        """
        Interview explanation:
        A node is good if all child-subtrees have equal size (leaves are good).
        DFS returns subtree sizes and counts good nodes along the way.

        Algorithm:
        - Build adjacency list rooted at 0.
        - DFS(u): gather child subtree sizes; good if all equal; return 1+sum.

        Complexity: O(n) time, O(n) space.
        """
        import sys

        sys.setrecursionlimit(10**6)
        n = len(edges) + 1
        g: List[List[int]] = [[] for _ in range(n)]
        for a, b in edges:
            g[a].append(b)
            g[b].append(a)

        ans = 0

        def dfs(u: int, parent: int) -> int:
            nonlocal ans
            sizes = []
            total = 1
            for v in g[u]:
                if v == parent:
                    continue
                sz = dfs(v, u)
                sizes.append(sz)
                total += sz
            if len(set(sizes)) <= 1:
                ans += 1
            return total

        dfs(0, -1)
        return ans
# @lc code=end
