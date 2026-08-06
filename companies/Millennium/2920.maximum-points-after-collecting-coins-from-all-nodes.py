#
# @lc app=leetcode id=2920 lang=python3
#
# [2920] Maximum Points After Collecting Coins From All Nodes
#
# https://leetcode.com/problems/maximum-points-after-collecting-coins-from-all-nodes/description/
#
# algorithms
# Hard (36.53%)
# Likes:    254
# Dislikes: 19
# Total Accepted:    11.9K
# Total Submissions: 32.7K
# Testcase Example:  "[[0,1],[1,2],[2,3]]\n[10,10,3,3]\n5"
#
#
# There exists an undirected tree rooted at node 0 with n nodes labeled
# from 0 to n - 1. You are given a 2D integer array edges of length n - 1,
# where edges[i] = [a_i, b_i] indicates that there is an edge between
# nodes a_i and b_i in the tree. You are also given a 0-indexed array
# coins of size n where coins[i] indicates the number of coins in the
# vertex i, and an integer k.
#
# Starting from the root, you have to collect all the coins such that the
# coins at a node can only be collected if the coins of its ancestors have
# been already collected.
#
# Coins at node_i can be collected in one of the following ways:
#
# Collect all the coins, but you will get coins[i] - k points. If coins[i]
# - k is negative then you will lose abs(coins[i] - k) points.
#
# Collect all the coins, but you will get floor(coins[i] / 2) points. If
# this way is used, then for all the node_j present in the subtree of
# node_i, coins[j] will get reduced to floor(coins[j] / 2).
#
# Return the maximum points you can get after collecting the coins from
# all the tree nodes.
#
# Example 1:
#
# Input: edges = [[0,1],[1,2],[2,3]], coins = [10,10,3,3], k = 5
# Output: 11
# Explanation:
# Collect all the coins from node 0 using the first way. Total points = 10
# - 5 = 5.
# Collect all the coins from node 1 using the first way. Total points = 5
# + (10 - 5) = 10.
# Collect all the coins from node 2 using the second way so coins left at
# node 3 will be floor(3 / 2) = 1. Total points = 10 + floor(3 / 2) = 11.
# Collect all the coins from node 3 using the second way. Total points =
# 11 + floor(1 / 2) = 11.
# It can be shown that the maximum points we can get after collecting
# coins from all the nodes is 11.
#
# Example 2:
#
# Input: edges = [[0,1],[0,2]], coins = [8,4,4], k = 0
# Output: 16
# Explanation:
# Coins will be collected from all the nodes using the first way.
# Therefore, total points = (8 - 0) + (4 - 0) + (4 - 0) = 16.
#
# Constraints:
#
# n == coins.length
#
# 2 <= n <= 10^5
#
# 0 <= coins[i] <= 10^4
#
# edges.length == n - 1
#
# 0 <= edges[i][0], edges[i][1] < n
#
# 0 <= k <= 10^4
#

# @lc code=start
import sys
from functools import lru_cache
from typing import List


class Solution:
    def maximumPoints(
        self, edges: List[List[int]], coins: List[int], k: int
    ) -> int:
        """
        Interview explanation:
        Tree rooted at 0. Collect every node after ancestors. At a node with
        current coins c (after ancestor halvings): take c-k, or take c//2 and
        halve the whole subtree further. Maximize total points.

        Algorithm:
        - Build children lists; tree DP state (node, halvings). coins[i] <= 1e4
          so halvings > ~14 are zero. Memoize both choices.

        Complexity: O(n * log C) time/space.
        """
        sys.setrecursionlimit(10**6)
        n = len(coins)
        g = [[] for _ in range(n)]
        for a, b in edges:
            g[a].append(b)
            g[b].append(a)
        children = [[] for _ in range(n)]

        def build(u: int, p: int) -> None:
            for v in g[u]:
                if v != p:
                    children[u].append(v)
                    build(v, u)

        build(0, -1)

        @lru_cache(None)
        def dfs(u: int, h: int) -> int:
            if h >= 14:
                return 0
            cur = coins[u] >> h
            op1 = cur - k + sum(dfs(v, h) for v in children[u])
            op2 = (cur // 2) + sum(dfs(v, h + 1) for v in children[u])
            return max(op1, op2)

        return dfs(0, 0)
# @lc code=end
