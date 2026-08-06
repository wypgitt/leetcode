#
# @lc app=leetcode id=2316 lang=python3
#
# [2316] Count Unreachable Pairs of Nodes in an Undirected Graph
#
# https://leetcode.com/problems/count-unreachable-pairs-of-nodes-in-an-undirected-graph/description/
#
# algorithms
# Medium (50.16%)
# Likes:    2298
# Dislikes: 56
# Total Accepted:    125.5K
# Total Submissions: 250.2K
# Testcase Example:  "3\n[[0,1],[0,2],[1,2]]"
#
# You are given an integer n. There is an undirected graph with n nodes,
# numbered from 0 to n - 1. You are given a 2D integer array edges where
# edges[i] = [a_i, b_i] denotes that there exists an undirected edge connecting
# nodes a_i and b_i.
#
# Return the number of pairs of different nodes that are unreachable from each
# other.
#
#
#
# Example 1:
#
# Input: n = 3, edges = [[0,1],[0,2],[1,2]]
# Output: 0
# Explanation: There are no pairs of nodes that are unreachable from each other.
# Therefore, we return 0.
#
# Example 2:
#
# Input: n = 7, edges = [[0,2],[0,5],[2,4],[1,6],[5,4]]
# Output: 14
# Explanation: There are 14 pairs of nodes that are unreachable from each other:
# [[0,1],[0,3],[0,6],[1,2],[1,3],[1,4],[1,5],[2,3],[2,6],[3,4],[3,5],[3,6],[4,6],[5,6]].
# Therefore, we return 14.
#
#
#
# Constraints:
#
#
# 1 <= n <= 10^5
#
#
# 0 <= edges.length <= 2 * 10^5
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
# There are no repeated edges.
#

# @lc code=start
from typing import List
from collections import defaultdict, deque


class Solution:
    def countPairs(self, n: int, edges: List[List[int]]) -> int:
        """
        Interview explanation:
        Count unordered pairs of nodes that cannot reach each other.

        Algorithm:
        - Find connected component sizes (DFS/BFS/UF). Answer =
          total_pairs - sum(size_i choose 2) equivalently
          accumulate rem * size while rem decreases.

        Complexity: O(n + m) time, O(n + m) space.
        """
        g = defaultdict(list)
        for u, v in edges:
            g[u].append(v)
            g[v].append(u)
        seen = [False] * n
        sizes = []
        for i in range(n):
            if seen[i]:
                continue
            stack = [i]
            seen[i] = True
            sz = 0
            while stack:
                u = stack.pop()
                sz += 1
                for v in g[u]:
                    if not seen[v]:
                        seen[v] = True
                        stack.append(v)
            sizes.append(sz)
        ans = 0
        rem = n
        for sz in sizes:
            rem -= sz
            ans += sz * rem
        return ans

    def countPairs_dfs(self, n: int, edges: List[List[int]]) -> int:
        """
        Interview explanation:
        DFS component sizing alternate.

        Algorithm:
        - Iterative DFS for each component; multiply sizes across cuts.

        Complexity: O(n + m) time, O(n + m) space.
        """
        return self.countPairs(n, edges)

    def countPairs_bfs(self, n: int, edges: List[List[int]]) -> int:
        """
        Interview explanation:
        BFS to size components, then same pair formula.

        Algorithm:
        - Queue BFS per unseen node; accumulate sz * remaining.

        Complexity: O(n + m) time, O(n + m) space.
        """
        g = defaultdict(list)
        for u, v in edges:
            g[u].append(v)
            g[v].append(u)
        seen = [False] * n
        ans = 0
        rem = n
        for i in range(n):
            if seen[i]:
                continue
            q = deque([i])
            seen[i] = True
            sz = 0
            while q:
                u = q.popleft()
                sz += 1
                for v in g[u]:
                    if not seen[v]:
                        seen[v] = True
                        q.append(v)
            rem -= sz
            ans += sz * rem
        return ans

    def countPairs_uf(self, n: int, edges: List[List[int]]) -> int:
        """
        Interview explanation:
        Union-Find component sizes, then unreachable pairs.

        Algorithm:
        - Union edges; count root sizes; apply sz * rem formula.

        Complexity: O((n+m) α(n)) time, O(n) space.
        """
        parent = list(range(n))
        size = [1] * n

        def find(x: int) -> int:
            while parent[x] != x:
                parent[x] = parent[parent[x]]
                x = parent[x]
            return x

        for u, v in edges:
            pu, pv = find(u), find(v)
            if pu != pv:
                if size[pu] < size[pv]:
                    pu, pv = pv, pu
                parent[pv] = pu
                size[pu] += size[pv]
        ans = 0
        rem = n
        for i in range(n):
            if find(i) == i:
                rem -= size[i]
                ans += size[i] * rem
        return ans
# @lc code=end
