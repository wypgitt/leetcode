#
# @lc app=leetcode id=839 lang=python3
#
# [839] Similar String Groups
#
# https://leetcode.com/problems/similar-string-groups/description/
#
# algorithms
# Hard (56.48%)
# Likes:    2479
# Dislikes: 217
# Total Accepted:    146K
# Total Submissions: 259K
# Testcase Example:  "[\"tars\",\"rats\",\"arts\",\"star\"]"
#
# Two strings, X and Y, are considered similar if either they are identical or
# we can make them equivalent by swapping at most two letters (in distinct
# positions) within the string X.
#
# For example, "tars" and "rats" are similar (swapping at positions 0 and 2),
# and "rats" and "arts" are similar, but "star" is not similar to "tars",
# "rats", or "arts".
#
# Together, these form two connected groups by similarity: {"tars", "rats",
# "arts"} and {"star"}. Notice that "tars" and "arts" are in the same group
# even though they are not similar. Formally, each group is such that a word is
# in the group if and only if it is similar to at least one other word in the
# group.
#
# We are given a list strs of strings where every string in strs is an anagram
# of every other string in strs. How many groups are there?
#
# Example 1:
#
# Input: strs = ["tars","rats","arts","star"]
# Output: 2
#
# Example 2:
#
# Input: strs = ["omv","ovm"]
# Output: 1
#
# Constraints:
#
# 1 <= strs.length <= 300
#
# 1 <= strs[i].length <= 300
#
# strs[i] consists of lowercase letters only.
#
# All words in strs have the same length and are anagrams of each other.
#

# @lc code=start

from typing import List


class Solution:
    def numSimilarGroups(self, strs: List[str]) -> int:
        """
        Interview explanation:
        Two strings similar if equal or differ in exactly two positions (one
        swap). Groups = connected components. Union-Find on indices when similar.

        Algorithm (Union-Find):
        - For each pair i<j, if similar union; count roots.

        Complexity: O(n^2 * L * α(n)) time, O(n) space.
        """
        n = len(strs)
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

        def similar(a: str, b: str) -> bool:
            diff = 0
            for x, y in zip(a, b):
                if x != y:
                    diff += 1
                    if diff > 2:
                        return False
            return diff == 0 or diff == 2

        for i in range(n):
            for j in range(i + 1, n):
                if similar(strs[i], strs[j]):
                    union(i, j)
        return len({find(i) for i in range(n)})

    def numSimilarGroups_dfs(self, strs: List[str]) -> int:
        """
        Interview explanation:
        Alternate: build similarity graph and DFS/BFS count components.

        Algorithm:
        - Edges when similar; DFS mark visited; count starts.

        Complexity: O(n^2 * L) time, O(n^2) space worst for adj.
        """
        n = len(strs)

        def similar(a: str, b: str) -> bool:
            diff = 0
            for x, y in zip(a, b):
                if x != y:
                    diff += 1
                    if diff > 2:
                        return False
            return diff == 0 or diff == 2

        g = [[] for _ in range(n)]
        for i in range(n):
            for j in range(i + 1, n):
                if similar(strs[i], strs[j]):
                    g[i].append(j)
                    g[j].append(i)
        seen = [False] * n

        def dfs(u: int) -> None:
            seen[u] = True
            for v in g[u]:
                if not seen[v]:
                    dfs(v)

        groups = 0
        for i in range(n):
            if not seen[i]:
                groups += 1
                dfs(i)
        return groups
# @lc code=end
