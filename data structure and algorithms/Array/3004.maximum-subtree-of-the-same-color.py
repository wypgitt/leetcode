#
# @lc app=leetcode id=3004 lang=python3
#
# [3004] Maximum Subtree of the Same Color
#
# https://leetcode.com/problems/maximum-subtree-of-the-same-color/description/
#
# algorithms
# Medium (58.92%)
# Likes:    25
# Dislikes: 0
# Total Accepted:    2.6K
# Total Submissions: 4.4K
# Testcase Example:  "[[0,1],[0,2],[0,3]]\n[1,1,2,3]"
#
#
# You are given a 2D integer array edges representing a tree with n nodes,
# numbered from 0 to n - 1, rooted at node 0, where edges[i] = [u_i, v_i]
# means there is an edge between the nodes v_i and u_i.
#
# You are also given a 0-indexed integer array colors of size n, where
# colors[i] is the color assigned to node i.
#
# We want to find a node v such that every node in the subtree of v has
# the same color.
#
# Return the size of such subtree with the maximum number of nodes
# possible.
#
# Example 1:
#
# Input: edges = [[0,1],[0,2],[0,3]], colors = [1,1,2,3]
# Output: 1
# Explanation: Each color is represented as: 1 -> Red, 2 -> Green, 3 ->
# Blue. We can see that the subtree rooted at node 0 has children with
# different colors. Any other subtree is of the same color and has a size
# of 1. Hence, we return 1.
#
# Example 2:
#
# Input: edges = [[0,1],[0,2],[0,3]], colors = [1,1,1,1]
# Output: 4
# Explanation: The whole tree has the same color, and the subtree rooted
# at node 0 has the most number of nodes which is 4. Hence, we return 4.
#
# Example 3:
#
# Input: edges = [[0,1],[0,2],[2,3],[2,4]], colors = [1,2,3,3,3]
# Output: 3
# Explanation: Each color is represented as: 1 -> Red, 2 -> Green, 3 ->
# Blue. We can see that the subtree rooted at node 0 has children with
# different colors. Any other subtree is of the same color, but the
# subtree rooted at node 2 has a size of 3 which is the maximum. Hence, we
# return 3.
#
# Constraints:
#
# n == edges.length + 1
#
# 1 <= n <= 5 * 10^4
#
# edges[i] == [u_i, v_i]
#
# 0 <= u_i, v_i < n
#
# colors.length == n
#
# 1 <= colors[i] <= 10^5
#
# The input is generated such that the graph represented by edges is a
# tree.
#

# @lc code=start

from typing import List


class Solution:
    def maximumSubtreeSize(self, edges: List[List[int]], colors: List[int]) -> int:
        """
        Interview explanation:
        Find the largest subtree (rooted at some v) where every node shares one
        color. DFS returns size and whether the subtree is monochromatic.

        Algorithm:
        - Build adjacency list for the tree rooted at 0.
        - DFS(u): aggregate child sizes; mono iff every child subtree is mono and
          matches colors[u].
        - Track the maximum size among monochromatic subtrees.

        Complexity: O(n) time, O(n) space.
        """
        n = len(colors)
        g: List[List[int]] = [[] for _ in range(n)]
        for u, v in edges:
            g[u].append(v)
            g[v].append(u)

        ans = 1

        def dfs(u: int, parent: int) -> tuple[int, bool]:
            nonlocal ans
            size = 1
            mono = True
            for v in g[u]:
                if v == parent:
                    continue
                child_size, child_mono = dfs(v, u)
                size += child_size
                if not child_mono or colors[v] != colors[u]:
                    mono = False
            if mono:
                ans = max(ans, size)
            return size, mono

        dfs(0, -1)
        return ans
# @lc code=end
