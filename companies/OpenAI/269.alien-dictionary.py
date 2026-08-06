#
# @lc app=leetcode id=269 lang=python3
#
# [269] Alien Dictionary
#
# https://leetcode.com/problems/alien-dictionary/description/
#
# algorithms
# Hard (37.28%)
# Likes:    4687
# Dislikes: 1040
# Total Accepted:    496.3K
# Total Submissions: 1.3M
# Testcase Example:  "[\"wrt\",\"wrf\",\"er\",\"ett\",\"rftt\"]"
#
#
# There is a new alien language that uses the English alphabet. However,
# the order of the letters is unknown to you.
#
# You are given a list of strings words from the alien language's
# dictionary. Now it is claimed that the strings in words are sorted
# lexicographically by the rules of this new language.
#
# If this claim is incorrect, and the given arrangement of string in words
# cannot correspond to any order of letters, return "".
#
# Otherwise, return a string of the unique letters in the new alien
# language sorted in lexicographically increasing order by the new
# language's rules. If there are multiple solutions, return any of them.
#
# Example 1:
#
# Input: words = ["wrt","wrf","er","ett","rftt"]
# Output: "wertf"
#
# Example 2:
#
# Input: words = ["z","x"]
# Output: "zx"
#
# Example 3:
#
# Input: words = ["z","x","z"]
# Output: ""
# Explanation: The order is invalid, so return "".
#
# Constraints:
#
# 1 <= words.length <= 100
#
# 1 <= words[i].length <= 100
#
# words[i] consists of only lowercase English letters.
#
# @lc code=start
from collections import defaultdict, deque
from typing import List


class Solution:
    def alienOrder(self, words: List[str]) -> str:
        """
        Interview explanation:
        Derive character precedence from adjacent word pairs, then topological
        sort. Invalid if a longer word precedes its prefix, or the graph has a cycle.

        Algorithm (Kahn / BFS — primary):
        - Build directed edges from first differing chars of consecutive words.
        - Track indegrees; repeatedly pop zero-indegree nodes (queue).
        - If processed count < alphabet size, cycle → "".

        Complexity: O(C) time and space for total characters C across words.
        """
        graph = defaultdict(set)
        indegree = {}
        for w in words:
            for c in w:
                indegree.setdefault(c, 0)

        for w1, w2 in zip(words, words[1:]):
            if len(w1) > len(w2) and w1.startswith(w2):
                return ""
            for a, b in zip(w1, w2):
                if a != b:
                    if b not in graph[a]:
                        graph[a].add(b)
                        indegree[b] += 1
                    break

        q = deque([c for c, d in indegree.items() if d == 0])
        order = []
        while q:
            c = q.popleft()
            order.append(c)
            for nei in graph[c]:
                indegree[nei] -= 1
                if indegree[nei] == 0:
                    q.append(nei)

        return "".join(order) if len(order) == len(indegree) else ""

    def alienOrderDFS(self, words: List[str]) -> str:
        """
        Interview explanation:
        Alternate: DFS topological sort with 3-color cycle detection
        (white/gray/black). Post-order append then reverse.

        Complexity: O(C) time and space.
        """
        graph = defaultdict(set)
        chars = set()
        for w in words:
            chars.update(w)

        for w1, w2 in zip(words, words[1:]):
            if len(w1) > len(w2) and w1.startswith(w2):
                return ""
            for a, b in zip(w1, w2):
                if a != b:
                    graph[a].add(b)
                    break

        WHITE, GRAY, BLACK = 0, 1, 2
        color = {c: WHITE for c in chars}
        order = []
        cycle = False

        def dfs(c: str) -> None:
            nonlocal cycle
            if cycle:
                return
            color[c] = GRAY
            for nei in graph[c]:
                if color[nei] == GRAY:
                    cycle = True
                    return
                if color[nei] == WHITE:
                    dfs(nei)
                    if cycle:
                        return
            color[c] = BLACK
            order.append(c)

        for c in list(chars):
            if color[c] == WHITE:
                dfs(c)
                if cycle:
                    return ""
        return "".join(reversed(order))
# @lc code=end

