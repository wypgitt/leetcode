#
# @lc app=leetcode id=685 lang=python3
#
# [685] Redundant Connection II
#
# https://leetcode.com/problems/redundant-connection-ii/description/
#
# algorithms
# Hard (36.45%)
# Likes:    2552
# Dislikes: 332
# Total Accepted:    95.3K
# Total Submissions: 261K
# Testcase Example:  "[[1,2],[1,3],[2,3]]"
#
# In this problem, a rooted tree is a directed graph such that, there is
# exactly one node (the root) for which all other nodes are descendants of this
# node, plus every node has exactly one parent, except for the root node which
# has no parents.
#
# The given input is a directed graph that started as a rooted tree with n
# nodes (with distinct values from 1 to n), with one additional directed edge
# added. The added edge has two different vertices chosen from 1 to n, and was
# not an edge that already existed.
#
# The resulting graph is given as a 2D-array of edges. Each element of edges is
# a pair [u_i, v_i] that represents a directed edge connecting nodes u_i and
# v_i, where u_i is a parent of child v_i.
#
# Return an edge that can be removed so that the resulting graph is a rooted
# tree of n nodes. If there are multiple answers, return the answer that occurs
# last in the given 2D-array.
#
# Example 1:
#
# Input: edges = [[1,2],[1,3],[2,3]]
# Output: [2,3]
#
# Example 2:
#
# Input: edges = [[1,2],[2,3],[3,4],[4,1],[1,5]]
# Output: [4,1]
#
# Constraints:
#
# n == edges.length
#
# 3 <= n <= 1000
#
# edges[i].length == 2
#
# 1 <= u_i, v_i <= n
#
# u_i != v_i
#

# @lc code=start
from typing import List


class Solution:
    def findRedundantDirectedConnection(self, edges: List[List[int]]) -> List[int]:
        """
        Interview explanation:
        Directed tree + one extra edge. Cases: (1) a node with two parents, or
        (2) a cycle. Prefer removing the later edge that creates two parents if
        that also breaks the cycle; else remove the cycle edge via Union-Find.

        Algorithm:
        - Detect candidateA/candidateB if some node has two parents (skip 2nd
          edge temporarily).
        - Union-Find on remaining edges; if cycle found: if no double parent,
          return cycle edge; else return candidateA (first parent edge).
        - Else return candidateB (second parent edge).

        Complexity: O(n α(n)) time, O(n) space.
        """
        n = len(edges)
        parent = [0] * (n + 1)
        cand_a = cand_b = None
        for u, v in edges:
            if parent[v] == 0:
                parent[v] = u
            else:
                cand_a = [parent[v], v]
                cand_b = [u, v]
                break

        dsu = list(range(n + 1))

        def find(x: int) -> int:
            while dsu[x] != x:
                dsu[x] = dsu[dsu[x]]
                x = dsu[x]
            return x

        for u, v in edges:
            if cand_b and [u, v] == cand_b:
                continue
            ru, rv = find(u), find(v)
            if ru == rv:
                if cand_a:
                    return cand_a
                return [u, v]
            dsu[rv] = ru
        return cand_b
# @lc code=end
