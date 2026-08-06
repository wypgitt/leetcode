#
# @lc app=leetcode id=2603 lang=python3
#
# [2603] Collect Coins in a Tree
#
# https://leetcode.com/problems/collect-coins-in-a-tree/description/
#
# algorithms
# Hard (39.71%)
# Likes:    581
# Dislikes: 25
# Total Accepted:    18.7K
# Total Submissions: 47.1K
# Testcase Example:  "[1,0,0,0,0,1]\n[[0,1],[1,2],[2,3],[3,4],[4,5]]"
#
# There exists an undirected and unrooted tree with n nodes indexed from 0 to n
# - 1. You are given an integer n and a 2D integer array edges of length n - 1,
# where edges[i] = [a_i, b_i] indicates that there is an edge between nodes a_i
# and b_i in the tree. You are also given an array coins of size n where
# coins[i] can be either 0 or 1, where 1 indicates the presence of a coin in the
# vertex i.
#
# Initially, you choose to start at any vertex in the tree. Then, you can
# perform the following operations any number of times:
#
#
# Collect all the coins that are at a distance of at most 2 from the current
# vertex, or
#
#
# Move to any adjacent vertex in the tree.
#
# Find the minimum number of edges you need to go through to collect all the
# coins and go back to the initial vertex.
#
# Note that if you pass an edge several times, you need to count it into the
# answer several times.
#
#
#
# Example 1:
#
# Input: coins = [1,0,0,0,0,1], edges = [[0,1],[1,2],[2,3],[3,4],[4,5]]
# Output: 2
# Explanation: Start at vertex 2, collect the coin at vertex 0, move to vertex
# 3, collect the coin at vertex 5 then move back to vertex 2.
#
# Example 2:
#
# Input: coins = [0,0,0,1,1,0,0,1], edges =
# [[0,1],[0,2],[1,3],[1,4],[2,5],[5,6],[5,7]]
# Output: 2
# Explanation: Start at vertex 0, collect the coins at vertices 4 and 3, move to
# vertex 2,  collect the coin at vertex 7, then move back to vertex 0.
#
#
#
# Constraints:
#
#
# n == coins.length
#
#
# 1 <= n <= 3 * 10^4
#
#
# 0 <= coins[i] <= 1
#
#
# edges.length == n - 1
#
#
# edges[i].length == 2
#
#
# 0 <= a_i, b_i < n
#
#
# a_i != b_i
#
#
# edges represents a valid tree.
#

# @lc code=start
from typing import List
from collections import deque


class Solution:
    def collectTheCoins(self, coins: List[int], edges: List[List[int]]) -> int:
        """
        Interview explanation:
        Collect coins within distance 2 and return; minimize round-trip edges
        traversed. Trim useless leaves, then peel 2 layers the collector can
        cover remotely; remaining edges are each traversed twice.

        Algorithm:
        - Build adjacency; repeatedly remove leaves with no coins.
        - Trim two more layers of leaves from the remaining tree.
        - Answer is 2 * remaining_edges (0 if ≤1 nodes left).

        Complexity: O(n) time, O(n) space.
        """
        n = len(coins)
        if n == 0:
            return 0
        adj: List[set] = [set() for _ in range(n)]
        for a, b in edges:
            adj[a].add(b)
            adj[b].add(a)

        deg = [len(adj[i]) for i in range(n)]
        q = deque(i for i in range(n) if deg[i] == 1 and coins[i] == 0)
        remaining = n
        while q:
            u = q.popleft()
            remaining -= 1
            for v in list(adj[u]):
                adj[v].discard(u)
                adj[u].discard(v)
                deg[v] -= 1
                deg[u] -= 1
                if deg[v] == 1 and coins[v] == 0:
                    q.append(v)

        for _ in range(2):
            leaves = [i for i in range(n) if deg[i] == 1]
            for u in leaves:
                remaining -= 1
                for v in list(adj[u]):
                    adj[v].discard(u)
                    adj[u].discard(v)
                    deg[v] -= 1
                    deg[u] -= 1

        if remaining <= 1:
            return 0
        return 2 * (remaining - 1)
# @lc code=end
