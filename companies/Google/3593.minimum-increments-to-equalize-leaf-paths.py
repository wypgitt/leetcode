#
# @lc app=leetcode id=3593 lang=python3
#
# [3593] Minimum Increments to Equalize Leaf Paths
#
# https://leetcode.com/problems/minimum-increments-to-equalize-leaf-paths/description/
#
# algorithms
# Medium (40.89%)
# Likes:    152
# Dislikes: 15
# Total Accepted:    16.8K
# Total Submissions: 41.1K
# Testcase Example:  "3\n[[0,1],[0,2]]\n[2,1,3]"
#
#
# You are given an integer n and an undirected tree rooted at node 0 with
# n nodes numbered from 0 to n - 1. This is represented by a 2D array
# edges of length n - 1, where edges[i] = [u_i, v_i] indicates an edge
# from node u_i to v_i .
#
# Each node i has an associated cost given by cost[i], representing the
# cost to traverse that node.
#
# The score of a path is defined as the sum of the costs of all nodes
# along the path.
#
# Your goal is to make the scores of all root-to-leaf paths equal by
# increasing the cost of any number of nodes by any non-negative amount.
#
# Return the minimum number of nodes whose cost must be increased to make
# all root-to-leaf path scores equal.
#
# Example 1:
#
# Input: n = 3, edges = [[0,1],[0,2]], cost = [2,1,3]
#
# Output: 1
#
# Explanation:
#
# There are two root-to-leaf paths:
#
# Path 0 → 1 has a score of 2 + 1 = 3.
#
# Path 0 → 2 has a score of 2 + 3 = 5.
#
# To make all root-to-leaf path scores equal to 5, increase the cost of
# node 1 by 2.
#
# Only one node is increased, so the output is 1.
#
# Example 2:
#
# Input: n = 3, edges = [[0,1],[1,2]], cost = [5,1,4]
#
# Output: 0
#
# Explanation:
#
# There is only one root-to-leaf path:
#
# Path 0 → 1 → 2 has a score of 5 + 1 + 4 = 10.
#
# Since only one root-to-leaf path exists, all path costs are trivially
# equal, and the output is 0.
#
# Example 3:
#
# Input: n = 5, edges = [[0,4],[0,1],[1,2],[1,3]], cost = [3,4,1,1,7]
#
# Output: 1
#
# Explanation:
#
# There are three root-to-leaf paths:
#
# Path 0 → 4 has a score of 3 + 7 = 10.
#
# Path 0 → 1 → 2 has a score of 3 + 4 + 1 = 8.
#
# Path 0 → 1 → 3 has a score of 3 + 4 + 1 = 8.
#
# To make all root-to-leaf path scores equal to 10, increase the cost of
# node 1 by 2. Thus, the output is 1.
#
# Constraints:
#
# 2 <= n <= 10^5
#
# edges.length == n - 1
#
# edges[i] == [u_i, v_i]
#
# 0 <= u_i, v_i < n
#
# cost.length == n
#
# 1 <= cost[i] <= 10^9
#
# The input is generated such that edges represents a valid tree.
#

# @lc code=start

from typing import List


class Solution:
    def minIncrease(self, n: int, edges: List[List[int]], cost: List[int]) -> int:
        """
        Interview explanation:
        Equalize all root→leaf path sums to the global maximum. At each node,
        only children whose subtree max path is below the local max need an
        increment somewhere in that subtree.

        Algorithm:
        - DFS returns max root-path sum in the subtree (from this node downward).
        - Start ans = n-1; for each node subtract the count of children already
          at the max child-path (those need no new increment at that link).

        Complexity: O(n) time, O(n) space.
        """
        adj: List[List[int]] = [[] for _ in range(n)]
        for u, v in edges:
            adj[u].append(v)
            adj[v].append(u)

        ans = n - 1

        def dfs(u: int, p: int) -> int:
            nonlocal ans
            best = 0
            cnt = 0
            for v in adj[u]:
                if v == p:
                    continue
                child = dfs(v, u)
                if child < best:
                    continue
                if child > best:
                    best = child
                    cnt = 0
                cnt += 1
            ans -= cnt
            return best + cost[u]

        dfs(0, -1)
        return ans
# @lc code=end
