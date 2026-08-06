#
# @lc app=leetcode id=2508 lang=python3
#
# [2508] Add Edges to Make Degrees of All Nodes Even
#
# https://leetcode.com/problems/add-edges-to-make-degrees-of-all-nodes-even/description/
#
# algorithms
# Hard (36.82%)
# Likes:    369
# Dislikes: 63
# Total Accepted:    25.2K
# Total Submissions: 68.4K
# Testcase Example:  "5\n[[1,2],[2,3],[3,4],[4,2],[1,4],[2,5]]"
#
# There is an undirected graph consisting of n nodes numbered from 1 to n. You
# are given the integer n and a 2D array edges where edges[i] = [a_i, b_i]
# indicates that there is an edge between nodes a_i and b_i. The graph can be
# disconnected.
#
# You can add at most two additional edges (possibly none) to this graph so that
# there are no repeated edges and no self-loops.
#
# Return true if it is possible to make the degree of each node in the graph
# even, otherwise return false.
#
# The degree of a node is the number of edges connected to it.
#
#
#
# Example 1:
#
# Input: n = 5, edges = [[1,2],[2,3],[3,4],[4,2],[1,4],[2,5]]
# Output: true
# Explanation: The above diagram shows a valid way of adding an edge.
# Every node in the resulting graph is connected to an even number of edges.
#
# Example 2:
#
# Input: n = 4, edges = [[1,2],[3,4]]
# Output: true
# Explanation: The above diagram shows a valid way of adding two edges.
#
# Example 3:
#
# Input: n = 4, edges = [[1,2],[1,3],[1,4]]
# Output: false
# Explanation: It is not possible to obtain a valid graph with adding at most 2
# edges.
#
#
#
# Constraints:
#
#
# 3 <= n <= 10^5
#
#
# 2 <= edges.length <= 10^5
#
#
# edges[i].length == 2
#
#
# 1 <= a_i, b_i <= n
#
#
# a_i != b_i
#
#
# There are no repeated edges.
#

# @lc code=start
from typing import List


class Solution:
    def isPossible(self, n: int, edges: List[List[int]]) -> bool:
        """
        Interview explanation:
        Add at most 2 new edges (no loops/duplicates) so every node has even
        degree. Only 0, 2, or 4 odd-degree nodes are fixable.

        Algorithm:
        - Build adjacency sets; collect odd-degree nodes.
        - 0 odds: true.
        - 2 odds a,b: true if no edge a-b, else true if some c free from both.
        - 4 odds: true if some pairing of two non-edges exists.
        - Else false.

        Complexity: O(n + m) time, O(n + m) space.
        """
        g = [set() for _ in range(n + 1)]
        for a, b in edges:
            g[a].add(b)
            g[b].add(a)
        odds = [i for i in range(1, n + 1) if len(g[i]) % 2]
        k = len(odds)
        if k == 0:
            return True
        if k == 2:
            a, b = odds
            if b not in g[a]:
                return True
            for c in range(1, n + 1):
                if c != a and c != b and c not in g[a] and c not in g[b]:
                    return True
            return False
        if k == 4:
            a, b, c, d = odds
            return (
                (b not in g[a] and d not in g[c])
                or (c not in g[a] and d not in g[b])
                or (d not in g[a] and c not in g[b])
            )
        return False
# @lc code=end
