#
# @lc app=leetcode id=1938 lang=python3
#
# [1938] Maximum Genetic Difference Query
#
# https://leetcode.com/problems/maximum-genetic-difference-query/description/
#
# algorithms
# Hard (47.77%)
# Likes:    425
# Dislikes: 24
# Total Accepted:    8.5K
# Total Submissions: 17.8K
# Testcase Example:  "[-1,0,1,1]"
#
# There is a rooted tree consisting of n nodes numbered 0 to n - 1. Each node's
# number denotes its unique genetic value (i.e. the genetic value of node x is
# x). The genetic difference between two genetic values is defined as the
# bitwise-XOR of their values. You are given the integer array parents, where
# parents[i] is the parent for node i. If node x is the root of the tree, then
# parents[x] == -1.
#
# You are also given the array queries where queries[i] = [node_i, val_i]. For
# each query i, find the maximum genetic difference between val_i and p_i,
# where p_i is the genetic value of any node that is on the path between node_i
# and the root (including node_i and the root). More formally, you want to
# maximize val_i XOR p_i.
#
# Return an array ans where ans[i] is the answer to the i^th query.
#
# Example 1:
#
# Input: parents = [-1,0,1,1], queries = [[0,2],[3,2],[2,5]]
# Output: [2,3,7]
# Explanation: The queries are processed as follows:
# - [0,2]: The node with the maximum genetic difference is 0, with a difference
# of 2 XOR 0 = 2.
# - [3,2]: The node with the maximum genetic difference is 1, with a difference
# of 2 XOR 1 = 3.
# - [2,5]: The node with the maximum genetic difference is 2, with a difference
# of 5 XOR 2 = 7.
#
# Example 2:
#
# Input: parents = [3,7,-1,2,0,7,0,2], queries = [[4,6],[1,15],[0,5]]
# Output: [6,14,7]
# Explanation: The queries are processed as follows:
# - [4,6]: The node with the maximum genetic difference is 0, with a difference
# of 6 XOR 0 = 6.
# - [1,15]: The node with the maximum genetic difference is 1, with a
# difference of 15 XOR 1 = 14.
# - [0,5]: The node with the maximum genetic difference is 2, with a difference
# of 5 XOR 2 = 7.
#
# Constraints:
#
# 2 <= parents.length <= 10^5
#
# 0 <= parents[i] <= parents.length - 1 for every node i that is not the root.
#
# parents[root] == -1
#
# 1 <= queries.length <= 3 * 10^4
#
# 0 <= node_i <= parents.length - 1
#
# 0 <= val_i <= 2 * 10^5
#

# @lc code=start
from typing import List
from collections import defaultdict


class Solution:
    def maxGeneticDifference(self, parents: List[int], queries: List[List[int]]) -> List[int]:
        """
        Interview explanation:
        Tree from parents (root parent=-1). Query (node,val): max val XOR of any
        ancestor-or-self of node. Offline: DFS from root inserting nodes into a
        binary XOR trie; answer queries at node; backtrack delete.

        Algorithm:
        - Build children; group queries by node. Trie insert/remove 20-bit values;
          query max XOR. DFS.

        Complexity: O((n+q) * 20) time/space.
        """
        n = len(parents)
        g = defaultdict(list)
        root = 0
        for i, p in enumerate(parents):
            if p == -1:
                root = i
            else:
                g[p].append(i)
        qmap = defaultdict(list)
        for qi, (node, val) in enumerate(queries):
            qmap[node].append((qi, val))
        ans = [0] * len(queries)

        class Trie:
            def __init__(self):
                self.ch = {}
                self.cnt = 0

            def add(self, x: int, d: int = 1):
                node = self
                node.cnt += d
                for b in range(19, -1, -1):
                    bit = (x >> b) & 1
                    if bit not in node.ch:
                        node.ch[bit] = Trie()
                    node = node.ch[bit]
                    node.cnt += d

            def maxxor(self, x: int) -> int:
                node = self
                res = 0
                for b in range(19, -1, -1):
                    bit = (x >> b) & 1
                    want = 1 - bit
                    if want in node.ch and node.ch[want].cnt > 0:
                        res |= 1 << b
                        node = node.ch[want]
                    else:
                        node = node.ch[bit]
                return res

        trie = Trie()

        def dfs(u: int):
            trie.add(u, 1)
            for qi, val in qmap[u]:
                ans[qi] = trie.maxxor(val)
            for v in g[u]:
                dfs(v)
            trie.add(u, -1)

        dfs(root)
        return ans
# @lc code=end
