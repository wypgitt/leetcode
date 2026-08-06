#
# @lc app=leetcode id=3493 lang=python3
#
# [3493] Properties Graph
#
# https://leetcode.com/problems/properties-graph/description/
#
# algorithms
# Medium (49.18%)
# Likes:    102
# Dislikes: 17
# Total Accepted:    26.9K
# Total Submissions: 54.7K
# Testcase Example:  "[[1,2],[1,1],[3,4],[4,5],[5,6],[7,7]]\n1"
#
#
# You are given a 2D integer array properties having dimensions n x m and
# an integer k.
#
# Define a function intersect(a, b) that returns the number of distinct
# integers common to both arrays a and b.
#
# Construct an undirected graph where each index i corresponds to
# properties[i]. There is an edge between node i and node j if and only if
# intersect(properties[i], properties[j]) >= k, where i and j are in the
# range [0, n - 1] and i != j.
#
# Return the number of connected components in the resulting graph.
#
# Example 1:
#
# Input: properties = [[1,2],[1,1],[3,4],[4,5],[5,6],[7,7]], k = 1
#
# Output: 3
#
# Explanation:
#
# The graph formed has 3 connected components:
#
# Example 2:
#
# Input: properties = [[1,2,3],[2,3,4],[4,3,5]], k = 2
#
# Output: 1
#
# Explanation:
#
# The graph formed has 1 connected component:
#
# Example 3:
#
# Input: properties = [[1,1],[1,1]], k = 2
#
# Output: 2
#
# Explanation:
#
# intersect(properties[0], properties[1]) = 1, which is less than k. This
# means there is no edge between properties[0] and properties[1] in the
# graph.
#
# Constraints:
#
# 1 <= n == properties.length <= 100
#
# 1 <= m == properties[i].length <= 100
#
# 1 <= properties[i][j] <= 100
#
# 1 <= k <= m
#

# @lc code=start
from typing import List


class Solution:
    def numberOfComponents(self, properties: List[List[int]], k: int) -> int:
        """
        Interview explanation:
        Edge between i,j iff |set(properties[i]) ∩ set(properties[j])| ≥ k.
        Count connected components.

        Algorithm:
        - Convert rows to sets; Union-Find / DFS over pairs with enough overlap.

        Complexity: O(n^2 * m) time (n,m ≤ 100), O(n) space.
        """
        n = len(properties)
        sets = [set(row) for row in properties]
        parent = list(range(n))

        def find(x: int) -> int:
            while parent[x] != x:
                parent[x] = parent[parent[x]]
                x = parent[x]
            return x

        def union(a: int, b: int) -> None:
            ra, rb = find(a), find(b)
            if ra != rb:
                parent[rb] = ra

        for i in range(n):
            for j in range(i + 1, n):
                if len(sets[i] & sets[j]) >= k:
                    union(i, j)

        return len({find(i) for i in range(n)})

    def numberOfComponents_dfs(self, properties: List[List[int]], k: int) -> int:
        """
        Interview explanation:
        Alternate: build adjacency list then DFS/BFS component count.

        Algorithm:
        - Pairwise edges via set intersection; DFS unmarked nodes.

        Complexity: O(n^2 * m) time, O(n^2) space for edges.
        """
        n = len(properties)
        sets = [set(row) for row in properties]
        g = [[] for _ in range(n)]
        for i in range(n):
            for j in range(i + 1, n):
                if len(sets[i] & sets[j]) >= k:
                    g[i].append(j)
                    g[j].append(i)

        seen = [False] * n

        def dfs(u: int) -> None:
            seen[u] = True
            for v in g[u]:
                if not seen[v]:
                    dfs(v)

        comps = 0
        for i in range(n):
            if not seen[i]:
                comps += 1
                dfs(i)
        return comps
# @lc code=end
