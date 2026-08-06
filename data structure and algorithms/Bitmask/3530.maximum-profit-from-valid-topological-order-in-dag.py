#
# @lc app=leetcode id=3530 lang=python3
#
# [3530] Maximum Profit from Valid Topological Order in DAG
#
# https://leetcode.com/problems/maximum-profit-from-valid-topological-order-in-dag/description/
#
# algorithms
# Hard (30.59%)
# Likes:    71
# Dislikes: 5
# Total Accepted:    6.5K
# Total Submissions: 21.4K
# Testcase Example:  "2\n[[0,1]]\n[2,3]"
#
#
# You are given a Directed Acyclic Graph (DAG) with n nodes labeled from 0
# to n - 1, represented by a 2D array edges, where edges[i] = [u_i, v_i]
# indicates a directed edge from node u_i to v_i. Each node has an
# associated score given in an array score, where score[i] represents the
# score of node i.
#
# You must process the nodes in a valid topological order. Each node is
# assigned a 1-based position in the processing order.
#
# The profit is calculated by summing up the product of each node's score
# and its position in the ordering.
#
# Return the maximum possible profit achievable with an optimal
# topological order.
#
# A topological order of a DAG is a linear ordering of its nodes such that
# for every directed edge u → v, node u comes before v in the ordering.
#
# Example 1:
#
# Input: n = 2, edges = [[0,1]], score = [2,3]
#
# Output: 8
#
# Explanation:
#
# Node 1 depends on node 0, so a valid order is [0, 1].
#
#                         Node
#                         Processing Order
#                         Score
#                         Multiplier
#                         Profit Calculation
#
#                         0
#                         1st
#                         2
#                         1
#                         2 × 1 = 2
#
#                         1
#                         2nd
#                         3
#                         2
#                         3 × 2 = 6
#
# The maximum total profit achievable over all valid topological orders is
# 2 + 6 = 8.
#
# Example 2:
#
# Input: n = 3, edges = [[0,1],[0,2]], score = [1,6,3]
#
# Output: 25
#
# Explanation:
#
# Nodes 1 and 2 depend on node 0, so the most optimal valid order is [0,
# 2, 1].
#
#                         Node
#                         Processing Order
#                         Score
#                         Multiplier
#                         Profit Calculation
#
#                         0
#                         1st
#                         1
#                         1
#                         1 × 1 = 1
#
#                         2
#                         2nd
#                         3
#                         2
#                         3 × 2 = 6
#
#                         1
#                         3rd
#                         6
#                         3
#                         6 × 3 = 18
#
# The maximum total profit achievable over all valid topological orders is
# 1 + 6 + 18 = 25.
#
# Constraints:
#
# 1 <= n == score.length <= 22
#
# 1 <= score[i] <= 10^5
#
# 0 <= edges.length <= n * (n - 1) / 2
#
# edges[i] == [u_i, v_i] denotes a directed edge from u_i to v_i.
#
# 0 <= u_i, v_i < n
#
# u_i != v_i
#
# The input graph is guaranteed to be a DAG.
#
# There are no duplicate edges.
#

# @lc code=start
from typing import List


class Solution:
    def maxProfit(self, n: int, edges: List[List[int]], score: List[int]) -> int:
        """
        Interview explanation:
        Profit is sum score[i] * (1-based position). With n ≤ 22, enumerate over
        subsets of processed nodes under topological constraints.

        Algorithm:
        - need[v] = bitmask of prerequisites of v.
        - dp[mask] = max profit after processing exactly the nodes in mask.
        - Transition: add any i ∉ mask whose need[i] ⊆ mask; position = |mask|+1.

        Complexity: O(2^n * n) time, O(2^n) space.
        """
        need = [0] * n
        for u, v in edges:
            need[v] |= 1 << u

        NEG = -10**18
        dp = [NEG] * (1 << n)
        dp[0] = 0
        full = (1 << n) - 1
        for mask in range(1 << n):
            if dp[mask] == NEG:
                continue
            pos = mask.bit_count() + 1
            for i in range(n):
                if mask & (1 << i):
                    continue
                if (need[i] & mask) == need[i]:
                    nxt = mask | (1 << i)
                    dp[nxt] = max(dp[nxt], dp[mask] + score[i] * pos)
        return dp[full]
# @lc code=end
