#
# @lc app=leetcode id=2479 lang=python3
#
# [2479] Maximum XOR of Two Non-Overlapping Subtrees
#
# https://leetcode.com/problems/maximum-xor-of-two-non-overlapping-subtrees/description/
#
# algorithms
# Hard (51.36%)
# Likes:    32
# Dislikes: 5
# Total Accepted:    1K
# Total Submissions: 2K
# Testcase Example:  "6\n[[0,1],[0,2],[1,3],[1,4],[2,5]]\n[2,8,3,6,2,5]"
#
#
# There is an undirected tree with n nodes labeled from 0 to n - 1. You
# are given the integer n and a 2D integer array edges of length n - 1,
# where edges[i] = [a_i, b_i] indicates that there is an edge between
# nodes a_i and b_i in the tree. The root of the tree is the node labeled
# 0.
#
# Each node has an associated value. You are given an array values of
# length n, where values[i] is the value of the i^th node.
#
# Select any two non-overlapping subtrees. Your score is the bitwise XOR
# of the sum of the values within those subtrees.
#
# Return the maximum possible score you can achieve. If it is impossible
# to find two nonoverlapping subtrees, return 0.
#
# Note that:
#
# The subtree of a node is the tree consisting of that node and all of its
# descendants.
#
# Two subtrees are non-overlapping if they do not share any common node.
#
# Example 1:
#
# Input: n = 6, edges = [[0,1],[0,2],[1,3],[1,4],[2,5]], values =
# [2,8,3,6,2,5]
# Output: 24
# Explanation: Node 1's subtree has sum of values 16, while node 2's
# subtree has sum of values 8, so choosing these nodes will yield a score
# of 16 XOR 8 = 24. It can be proved that is the maximum possible score we
# can obtain.
#
# Example 2:
#
# Input: n = 3, edges = [[0,1],[1,2]], values = [4,6,1]
# Output: 0
# Explanation: There is no possible way to select two non-overlapping
# subtrees, so we just return 0.
#
# Constraints:
#
# 2 <= n <= 5 * 10^4
#
# edges.length == n - 1
#
# 0 <= a_i, b_i < n
#
# values.length == n
#
# 1 <= values[i] <= 10^9
#
# It is guaranteed that edges represents a valid tree.
#
# @lc code=start
from typing import List
from collections import defaultdict


class Trie:
    def __init__(self):
        """
        Interview explanation:
        Binary trie node for 48-bit subtree sums (max XOR queries).

        Algorithm:
        - Two children for bits 0/1.

        Complexity: O(1) init.
        """
        self.children = [None, None]

    def insert(self, x: int) -> None:
        """
        Interview explanation:
        Insert subtree-sum into binary XOR trie.

        Algorithm:
        - Walk bits high to low creating nodes.

        Complexity: O(bits) per insert.
        """
        node = self
        for i in range(47, -1, -1):
            v = (x >> i) & 1
            if node.children[v] is None:
                node.children[v] = Trie()
            node = node.children[v]

    def search(self, x: int) -> int:
        """
        Interview explanation:
        Query max XOR of x against inserted values.

        Algorithm:
        - Prefer opposite bit at each level.

        Complexity: O(bits).
        """
        node = self
        res = 0
        for i in range(47, -1, -1):
            if node is None:
                return res
            v = (x >> i) & 1
            if node.children[v ^ 1]:
                res = (res << 1) | 1
                node = node.children[v ^ 1]
            else:
                res <<= 1
                node = node.children[v]
        return res


class Solution:
    def maxXor(self, n: int, edges: List[List[int]], values: List[int]) -> int:
        """
        Interview explanation:
        Premium. Tree rooted at 0; pick two non-overlapping subtrees maximizing
        XOR of their value-sums.

        Algorithm:
        - Compute subtree sums; DFS post-order insert finished subtrees into
          XOR trie before querying ancestors' candidates (disjoint by order).

        Complexity: O(n * bits) time, O(n * bits) space.
        """
        g = defaultdict(list)
        for a, b in edges:
            g[a].append(b)
            g[b].append(a)
        s = [0] * n

        def dfs1(i: int, fa: int) -> int:
            t = values[i]
            for j in g[i]:
                if j != fa:
                    t += dfs1(j, i)
            s[i] = t
            return t

        dfs1(0, -1)
        ans = 0
        tree = Trie()

        def dfs2(i: int, fa: int) -> None:
            nonlocal ans
            ans = max(ans, tree.search(s[i]))
            for j in g[i]:
                if j != fa:
                    dfs2(j, i)
            tree.insert(s[i])

        dfs2(0, -1)
        return ans
# @lc code=end

