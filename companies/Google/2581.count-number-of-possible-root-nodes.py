#
# @lc app=leetcode id=2581 lang=python3
#
# [2581] Count Number of Possible Root Nodes
#
# https://leetcode.com/problems/count-number-of-possible-root-nodes/description/
#
# algorithms
# Hard (48.79%)
# Likes:    328
# Dislikes: 11
# Total Accepted:    9.7K
# Total Submissions: 19.9K
# Testcase Example:  "[[0,1],[1,2],[1,3],[4,2]]\n[[1,3],[0,1],[1,0],[2,4]]\n3"
#
# Alice has an undirected tree with n nodes labeled from 0 to n - 1. The tree is
# represented as a 2D integer array edges of length n - 1 where edges[i] = [a_i,
# b_i] indicates that there is an edge between nodes a_i and b_i in the tree.
#
# Alice wants Bob to find the root of the tree. She allows Bob to make several
# guesses about her tree. In one guess, he does the following:
#
#
# Chooses two distinct integers u and v such that there exists an edge [u, v] in
# the tree.
#
#
# He tells Alice that u is the parent of v in the tree.
#
# Bob's guesses are represented by a 2D integer array guesses where guesses[j] =
# [u_j, v_j] indicates Bob guessed u_j to be the parent of v_j.
#
# Alice being lazy, does not reply to each of Bob's guesses, but just says that
# at least k of his guesses are true.
#
# Given the 2D integer arrays edges, guesses and the integer k, return the
# number of possible nodes that can be the root of Alice's tree. If there is no
# such tree, return 0.
#
#
#
# Example 1:
#
# Input: edges = [[0,1],[1,2],[1,3],[4,2]], guesses = [[1,3],[0,1],[1,0],[2,4]],
# k = 3
# Output: 3
# Explanation:
# Root = 0, correct guesses = [1,3], [0,1], [2,4]
# Root = 1, correct guesses = [1,3], [1,0], [2,4]
# Root = 2, correct guesses = [1,3], [1,0], [2,4]
# Root = 3, correct guesses = [1,0], [2,4]
# Root = 4, correct guesses = [1,3], [1,0]
# Considering 0, 1, or 2 as root node leads to 3 correct guesses.
#
# Example 2:
#
# Input: edges = [[0,1],[1,2],[2,3],[3,4]], guesses = [[1,0],[3,4],[2,1],[3,2]],
# k = 1
# Output: 5
# Explanation:
# Root = 0, correct guesses = [3,4]
# Root = 1, correct guesses = [1,0], [3,4]
# Root = 2, correct guesses = [1,0], [2,1], [3,4]
# Root = 3, correct guesses = [1,0], [2,1], [3,2], [3,4]
# Root = 4, correct guesses = [1,0], [2,1], [3,2]
# Considering any node as root will give at least 1 correct guess.
#
#
#
# Constraints:
#
#
# edges.length == n - 1
#
#
# 2 <= n <= 10^5
#
#
# 1 <= guesses.length <= 10^5
#
#
# 0 <= a_i, b_i, u_j, v_j <= n - 1
#
#
# a_i != b_i
#
#
# u_j != v_j
#
#
# edges represents a valid tree.
#
#
# guesses[j] is an edge of the tree.
#
#
# guesses is unique.
#
#
# 0 <= k <= guesses.length
#

# @lc code=start
from typing import List
from collections import defaultdict


class Solution:
    def rootCount(self, edges: List[List[int]], guesses: List[List[int]], k: int) -> int:
        """
        Interview explanation:
        Tree is undirected; guesses are directed parent->child claims. Count roots such
        that at least k guesses are correct. Use rerooting DP.

        Algorithm:
        - Build adjacency; put guesses in a set.
        - DFS compute correct guesses when rooted at 0.
        - Reroot: moving root across edge u-v flips whether guess (u,v)/(v,u) counts.

        Complexity: O(n + g) time, O(n + g) space.
        """
        n = len(edges) + 1
        g = defaultdict(list)
        for a, b in edges:
            g[a].append(b)
            g[b].append(a)
        guess_set = {(a, b) for a, b in guesses}

        def dfs(u, p):
            cnt = 0
            for v in g[u]:
                if v == p:
                    continue
                cnt += ((u, v) in guess_set) + dfs(v, u)
            return cnt

        base = dfs(0, -1)
        ans = 0

        def reroot(u, p, cur):
            nonlocal ans
            if cur >= k:
                ans += 1
            for v in g[u]:
                if v == p:
                    continue
                nxt = cur - ((u, v) in guess_set) + ((v, u) in guess_set)
                reroot(v, u, nxt)

        reroot(0, -1, base)
        return ans
# @lc code=end
