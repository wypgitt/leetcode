#
# @lc app=leetcode id=1202 lang=python3
#
# [1202] Smallest String With Swaps
#
# https://leetcode.com/problems/smallest-string-with-swaps/description/
#
# algorithms
# Medium (60.88%)
# Likes:    3940
# Dislikes: 166
# Total Accepted:    153K
# Total Submissions: 252K
# Testcase Example:  "\"dcab\""
#
# You are given a string s, and an array of pairs of indices in the string
# pairs where pairs[i] = [a, b] indicates 2 indices(0-indexed) of the string.
#
# You can swap the characters at any pair of indices in the given pairs any
# number of times.
#
# Return the lexicographically smallest string that s can be changed to after
# using the swaps.
#
# Example 1:
#
# Input: s = "dcab", pairs = [[0,3],[1,2]]
# Output: "bacd"
# Explaination:
# Swap s[0] and s[3], s = "bcad"
# Swap s[1] and s[2], s = "bacd"
#
# Example 2:
#
# Input: s = "dcab", pairs = [[0,3],[1,2],[0,2]]
# Output: "abcd"
# Explaination:
# Swap s[0] and s[3], s = "bcad"
# Swap s[0] and s[2], s = "acbd"
# Swap s[1] and s[2], s = "abcd"
#
# Example 3:
#
# Input: s = "cba", pairs = [[0,1],[1,2]]
# Output: "abc"
# Explaination:
# Swap s[0] and s[1], s = "bca"
# Swap s[1] and s[2], s = "bac"
# Swap s[0] and s[1], s = "abc"
#
# Constraints:
#
# 1 <= s.length <= 10^5
#
# 0 <= pairs.length <= 10^5
#
# 0 <= pairs[i][0], pairs[i][1] < s.length
#
# s only contains lower case English letters.
#


# @lc code=start
from typing import List
from collections import defaultdict

class Solution:
    def smallestStringWithSwaps(self, s: str, pairs: List[List[int]]) -> str:
        """
        Interview explanation:
        Swaps are transitive: connected indices form a component. Within each
        component, sort characters ascending and place them at sorted indices.

        Algorithm:
        - Union-Find on pairs; group indices by root; sort chars per group;
          write back into result array.

        Complexity: O((n+m) α(n) + n log n) time, O(n) space.
        """
        n = len(s)
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

        for a, b in pairs:
            union(a, b)

        groups: dict = defaultdict(list)
        for i in range(n):
            groups[find(i)].append(i)

        res = list(s)
        for idxs in groups.values():
            chars = sorted(res[i] for i in idxs)
            for i, ch in zip(sorted(idxs), chars):
                res[i] = ch
        return "".join(res)

    def smallestStringWithSwaps_dfs(self, s: str, pairs: List[List[int]]) -> str:
        """
        Interview explanation:
        Alternate: build undirected graph from pairs; DFS/BFS each component;
        sort characters and assign to sorted indices.

        Algorithm:
        - adj list; for each unvisited node DFS collect indices; sort & assign.

        Complexity: O(n log n + m) time, O(n+m) space.
        """
        n = len(s)
        adj = [[] for _ in range(n)]
        for a, b in pairs:
            adj[a].append(b)
            adj[b].append(a)
        visited = [False] * n
        res = list(s)

        def dfs(u: int, comp: list) -> None:
            visited[u] = True
            comp.append(u)
            for v in adj[u]:
                if not visited[v]:
                    dfs(v, comp)

        for i in range(n):
            if not visited[i]:
                comp = []
                dfs(i, comp)
                chars = sorted(res[j] for j in comp)
                for j, ch in zip(sorted(comp), chars):
                    res[j] = ch
        return "".join(res)
# @lc code=end
