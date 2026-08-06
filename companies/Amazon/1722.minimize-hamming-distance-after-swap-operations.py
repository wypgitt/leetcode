#
# @lc app=leetcode id=1722 lang=python3
#
# [1722] Minimize Hamming Distance After Swap Operations
#
# https://leetcode.com/problems/minimize-hamming-distance-after-swap-operations/description/
#
# algorithms
# Medium (69.63%)
# Likes:    1419
# Dislikes: 44
# Total Accepted:    94.6K
# Total Submissions: 136K
# Testcase Example:  "[1,2,3,4]"
#
# You are given two integer arrays, source and target, both of length n. You
# are also given an array allowedSwaps where each allowedSwaps[i] = [a_i, b_i]
# indicates that you are allowed to swap the elements at index a_i and index
# b_i (0-indexed) of array source. Note that you can swap elements at a
# specific pair of indices multiple times and in any order.
#
# The Hamming distance of two arrays of the same length, source and target, is
# the number of positions where the elements are different. Formally, it is the
# number of indices i for 0 <= i <= n-1 where source[i] != target[i]
# (0-indexed).
#
# Return the minimum Hamming distance of source and target after performing any
# amount of swap operations on array source.
#
# Example 1:
#
# Input: source = [1,2,3,4], target = [2,1,4,5], allowedSwaps = [[0,1],[2,3]]
# Output: 1
# Explanation: source can be transformed the following way:
# - Swap indices 0 and 1: source = [2,1,3,4]
# - Swap indices 2 and 3: source = [2,1,4,3]
# The Hamming distance of source and target is 1 as they differ in 1 position:
# index 3.
#
# Example 2:
#
# Input: source = [1,2,3,4], target = [1,3,2,4], allowedSwaps = []
# Output: 2
# Explanation: There are no allowed swaps.
# The Hamming distance of source and target is 2 as they differ in 2 positions:
# index 1 and index 2.
#
# Example 3:
#
# Input: source = [5,1,2,4,3], target = [1,5,4,2,3], allowedSwaps =
# [[0,4],[4,2],[1,3],[1,4]]
# Output: 0
#
# Constraints:
#
# n == source.length == target.length
#
# 1 <= n <= 10^5
#
# 1 <= source[i], target[i] <= 10^5
#
# 0 <= allowedSwaps.length <= 10^5
#
# allowedSwaps[i].length == 2
#
# 0 <= a_i, b_i <= n - 1
#
# a_i != b_i
#

# @lc code=start
from typing import List
from collections import Counter, defaultdict


class Solution:
    def minimumHammingDistance(self, source: List[int], target: List[int], allowedSwaps: List[List[int]]) -> int:
        """
        Interview explanation:
        Swaps form connected components (Union-Find). Within a component, values
        can be arbitrarily rearranged. Hamming distance contribution is positions
        where we cannot match target via multiset overlap.

        Algorithm:
        - UF on allowedSwaps; for each component, Counter(source) vs Counter(target);
          unmatched = sum (target counts not covered by source).
        - Answer = total unmatched across components (equals positions that differ
          after optimal rearrange).

        Complexity: O(n α(n) + |swaps|) time, O(n) space.
        """
        n = len(source)
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

        for a, b in allowedSwaps:
            union(a, b)

        comps = defaultdict(list)
        for i in range(n):
            comps[find(i)].append(i)

        ans = 0
        for idxs in comps.values():
            cs = Counter(source[i] for i in idxs)
            for i in idxs:
                if cs[target[i]]:
                    cs[target[i]] -= 1
                else:
                    ans += 1
        return ans


    def minimumHammingDistance_dfs(self, source: List[int], target: List[int], allowedSwaps: List[List[int]]) -> int:
        """
        Interview explanation:
        Alternate: build swap graph and DFS/BFS connected components instead of UF,
        then the same multiset matching per component.

        Algorithm:
        - adjacency from allowedSwaps; DFS mark components; Counter match vs target.

        Complexity: O(n + |swaps|) time, O(n) space.
        """
        n = len(source)
        g = [[] for _ in range(n)]
        for a, b in allowedSwaps:
            g[a].append(b)
            g[b].append(a)
        seen = [False] * n
        ans = 0
        for i in range(n):
            if seen[i]:
                continue
            stack = [i]
            seen[i] = True
            idxs = []
            while stack:
                u = stack.pop()
                idxs.append(u)
                for v in g[u]:
                    if not seen[v]:
                        seen[v] = True
                        stack.append(v)
            cs = Counter(source[j] for j in idxs)
            for j in idxs:
                if cs[target[j]]:
                    cs[target[j]] -= 1
                else:
                    ans += 1
        return ans

# @lc code=end
