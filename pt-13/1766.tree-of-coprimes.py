#
# @lc app=leetcode id=1766 lang=python3
#
# [1766] Tree of Coprimes
#
# https://leetcode.com/problems/tree-of-coprimes/description/
#
# algorithms
# Hard (44.63%)
# Likes:    434
# Dislikes: 37
# Total Accepted:    14.9K
# Total Submissions: 33.4K
# Testcase Example:  "[2,3,3,2]"
#
# There is a tree (i.e., a connected, undirected graph that has no cycles)
# consisting of n nodes numbered from 0 to n - 1 and exactly n - 1 edges. Each
# node has a value associated with it, and the root of the tree is node 0.
#
# To represent this tree, you are given an integer array nums and a 2D array
# edges. Each nums[i] represents the i^th node's value, and each edges[j] =
# [u_j, v_j] represents an edge between nodes u_j and v_j in the tree.
#
# Two values x and y are coprime if gcd(x, y) == 1 where gcd(x, y) is the
# greatest common divisor of x and y.
#
# An ancestor of a node i is any other node on the shortest path from node i to
# the root. A node is not considered an ancestor of itself.
#
# Return an array ans of size n, where ans[i] is the closest ancestor to node i
# such that nums[i] and nums[ans[i]] are coprime, or -1 if there is no such
# ancestor.
#
# Example 1:
#
# Input: nums = [2,3,3,2], edges = [[0,1],[1,2],[1,3]]
# Output: [-1,0,0,1]
# Explanation: In the above figure, each node's value is in parentheses.
# - Node 0 has no coprime ancestors.
# - Node 1 has only one ancestor, node 0. Their values are coprime (gcd(2,3) ==
# 1).
# - Node 2 has two ancestors, nodes 1 and 0. Node 1's value is not coprime
# (gcd(3,3) == 3), but node 0's
# value is (gcd(2,3) == 1), so node 0 is the closest valid ancestor.
# - Node 3 has two ancestors, nodes 1 and 0. It is coprime with node 1
# (gcd(3,2) == 1), so node 1 is its
# closest valid ancestor.
#
# Example 2:
#
# Input: nums = [5,6,10,2,3,6,15], edges =
# [[0,1],[0,2],[1,3],[1,4],[2,5],[2,6]]
# Output: [-1,0,-1,0,0,0,-1]
#
# Constraints:
#
# nums.length == n
#
# 1 <= nums[i] <= 50
#
# 1 <= n <= 10^5
#
# edges.length == n - 1
#
# edges[j].length == 2
#
# 0 <= u_j, v_j < n
#
# u_j != v_j
#

# @lc code=start
from typing import List
import math


class Solution:
    def getCoprimes(self, nums: List[int], edges: List[List[int]]) -> List[int]:
        """
        Interview explanation:
        For each node, find closest ancestor with gcd(value, nums[node])==1
        (or -1). Values are in 1..50 → precompute coprime pairs; DFS while
        keeping a stack of (depth, node) per value; query stacks of coprime
        values for the nearest ancestor.

        Algorithm:
        - Build tree; cop[v] = list of w with gcd(v,w)==1.
        - DFS: for node, best among stacks of cop[nums[node]]; push; recurse; pop.

        Complexity: O(n * Σ) with Σ≤50, O(n+Σ) space.
        """
        n = len(nums)
        g = [[] for _ in range(n)]
        for u, v in edges:
            g[u].append(v)
            g[v].append(u)
        cop = [[] for _ in range(51)]
        for a in range(1, 51):
            for b in range(1, 51):
                if math.gcd(a, b) == 1:
                    cop[a].append(b)
        stacks = [[] for _ in range(51)]  # (depth, index)
        ans = [-1] * n

        def dfs(u: int, parent: int, depth: int) -> None:
            val = nums[u]
            best_d, best_i = -1, -1
            for w in cop[val]:
                if stacks[w]:
                    d, i = stacks[w][-1]
                    if d > best_d:
                        best_d, best_i = d, i
            ans[u] = best_i
            stacks[val].append((depth, u))
            for v in g[u]:
                if v != parent:
                    dfs(v, u, depth + 1)
            stacks[val].pop()

        dfs(0, -1, 0)
        return ans
# @lc code=end
