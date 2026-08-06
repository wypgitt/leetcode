#
# @lc app=leetcode id=886 lang=python3
#
# [886] Possible Bipartition
#
# https://leetcode.com/problems/possible-bipartition/description/
#
# algorithms
# Medium (52.91%)
# Likes:    4958
# Dislikes: 120
# Total Accepted:    275K
# Total Submissions: 520K
# Testcase Example:  "4"
#
# We want to split a group of n people (labeled from 1 to n) into two groups of
# any size. Each person may dislike some other people, and they should not go
# into the same group.
#
# Given the integer n and the array dislikes where dislikes[i] = [a_i, b_i]
# indicates that the person labeled a_i does not like the person labeled b_i,
# return true if it is possible to split everyone into two groups in this way.
#
# Example 1:
#
# Input: n = 4, dislikes = [[1,2],[1,3],[2,4]]
# Output: true
# Explanation: The first group has [1,4], and the second group has [2,3].
#
# Example 2:
#
# Input: n = 3, dislikes = [[1,2],[1,3],[2,3]]
# Output: false
# Explanation: We need at least 3 groups to divide them. We cannot put them in
# two groups.
#
# Constraints:
#
# 1 <= n <= 2000
#
# 0 <= dislikes.length <= 10^4
#
# dislikes[i].length == 2
#
# 1 <= a_i < b_i <= n
#
# All the pairs of dislikes are unique.
#

# @lc code=start
from collections import defaultdict, deque
from typing import Dict, List


class Solution:
    def possibleBipartition(self, n: int, dislikes: List[List[int]]) -> bool:
        """
        Interview explanation:
        Dislike edges form undirected graph; bipartition possible iff graph is
        bipartite. BFS 2-color each component.

        Algorithm (BFS coloring):
        - Build adj. color[u]=0/1/-1. BFS; neighbor same color ⇒ False.

        Complexity: O(n+E) time, O(n+E) space.
        """
        graph: Dict[int, List[int]] = defaultdict(list)
        for a, b in dislikes:
            graph[a].append(b)
            graph[b].append(a)
        color = [-1] * (n + 1)
        for start in range(1, n + 1):
            if color[start] != -1:
                continue
            color[start] = 0
            q = deque([start])
            while q:
                u = q.popleft()
                for v in graph[u]:
                    if color[v] == -1:
                        color[v] = color[u] ^ 1
                        q.append(v)
                    elif color[v] == color[u]:
                        return False
        return True

    def possibleBipartition_dfs(self, n: int, dislikes: List[List[int]]) -> bool:
        """
        Interview explanation:
        Alternate classic: DFS coloring with same 2-color invariant.

        Algorithm:
        - dfs(u,c): color and recurse neighbors with c^1; conflict ⇒ False.

        Complexity: O(n+E) time, O(n+E) space.
        """
        graph: Dict[int, List[int]] = defaultdict(list)
        for a, b in dislikes:
            graph[a].append(b)
            graph[b].append(a)
        color = [-1] * (n + 1)

        def dfs(u: int, c: int) -> bool:
            color[u] = c
            for v in graph[u]:
                if color[v] == -1:
                    if not dfs(v, c ^ 1):
                        return False
                elif color[v] == color[u]:
                    return False
            return True

        for i in range(1, n + 1):
            if color[i] == -1 and not dfs(i, 0):
                return False
        return True
# @lc code=end

