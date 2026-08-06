#
# @lc app=leetcode id=1579 lang=python3
#
# [1579] Remove Max Number of Edges to Keep Graph Fully Traversable
#
# https://leetcode.com/problems/remove-max-number-of-edges-to-keep-graph-fully-traversable/description/
#
# algorithms
# Hard (70.12%)
# Likes:    2721
# Dislikes: 46
# Total Accepted:    148K
# Total Submissions: 211K
# Testcase Example:  "4"
#
# Alice and Bob have an undirected graph of n nodes and three types of edges:
#
# Type 1: Can be traversed by Alice only.
#
# Type 2: Can be traversed by Bob only.
#
# Type 3: Can be traversed by both Alice and Bob.
#
# Given an array edges where edges[i] = [type_i, u_i, v_i] represents a
# bidirectional edge of type type_i between nodes u_i and v_i, find the maximum
# number of edges you can remove so that after removing the edges, the graph
# can still be fully traversed by both Alice and Bob. The graph is fully
# traversed by Alice and Bob if starting from any node, they can reach all
# other nodes.
#
# Return the maximum number of edges you can remove, or return -1 if Alice and
# Bob cannot fully traverse the graph.
#
# Example 1:
#
# Input: n = 4, edges = [[3,1,2],[3,2,3],[1,1,3],[1,2,4],[1,1,2],[2,3,4]]
# Output: 2
# Explanation: If we remove the 2 edges [1,1,2] and [1,1,3]. The graph will
# still be fully traversable by Alice and Bob. Removing any additional edge
# will not make it so. So the maximum number of edges we can remove is 2.
#
# Example 2:
#
# Input: n = 4, edges = [[3,1,2],[3,2,3],[1,1,4],[2,1,4]]
# Output: 0
# Explanation: Notice that removing any edge will not make the graph fully
# traversable by Alice and Bob.
#
# Example 3:
#
# Input: n = 4, edges = [[3,2,3],[1,1,2],[2,3,4]]
# Output: -1
# Explanation: In the current graph, Alice cannot reach node 4 from the other
# nodes. Likewise, Bob cannot reach 1. Therefore it's impossible to make the
# graph fully traversable.
#
# Constraints:
#
# 1 <= n <= 10^5
#
# 1 <= edges.length <= min(10^5, 3 * n * (n - 1) / 2)
#
# edges[i].length == 3
#
# 1 <= type_i <= 3
#
# 1 <= u_i < v_i <= n
#
# All tuples (type_i, u_i, v_i) are distinct.
#

# @lc code=start
from typing import List


class Solution:
    def maxNumEdgesToRemove(self, n: int, edges: List[List[int]]) -> int:
        """
        Interview explanation:
        Edges type 1 Alice-only, 2 Bob-only, 3 both. Maximize removable edges
        so both still fully traverse. Use type-3 first (shared MST), then add
        type-1 for Alice and type-2 for Bob; unused edges are removable. If
        either not connected → -1.

        Algorithm (Union-Find dual):
        - UF Alice & Bob; add type 3 to both; count used.
        - Add type 1 to Alice-only UF; type 2 to Bob-only.
        - If both have n-1 unions total connectivity OK; return len(edges)-used.

        Complexity: O(E α(n)).
        """
        class UF:
            def __init__(self, n: int):
                self.p = list(range(n + 1))
                self.comps = n

            def find(self, x: int) -> int:
                while self.p[x] != x:
                    self.p[x] = self.p[self.p[x]]
                    x = self.p[x]
                return x

            def union(self, a: int, b: int) -> bool:
                ra, rb = self.find(a), self.find(b)
                if ra == rb:
                    return False
                self.p[rb] = ra
                self.comps -= 1
                return True

        alice, bob = UF(n), UF(n)
        used = 0
        for t, u, v in edges:
            if t == 3:
                au = alice.union(u, v)
                bu = bob.union(u, v)
                if au or bu:
                    used += 1
                # if both already connected, edge unused (au/bu both False)
        for t, u, v in edges:
            if t == 1 and alice.union(u, v):
                used += 1
            elif t == 2 and bob.union(u, v):
                used += 1
        if alice.comps > 1 or bob.comps > 1:
            return -1
        return len(edges) - used
# @lc code=end

