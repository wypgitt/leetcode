#
# @lc app=leetcode id=399 lang=python3
#
# [399] Evaluate Division
#
# https://leetcode.com/problems/evaluate-division/description/
#
# algorithms
# Medium (64.48%)
# Likes:    10302
# Dislikes: 1104
# Total Accepted:    738K
# Total Submissions: 1.1M
# Testcase Example:  "[[\"a\",\"b\"],[\"b\",\"c\"]]"
#
# You are given an array of variable pairs equations and an array of real
# numbers values, where equations[i] = [A_i, B_i] and values[i] represent the
# equation A_i / B_i = values[i]. Each A_i or B_i is a string that represents a
# single variable.
#
# You are also given some queries, where queries[j] = [C_j, D_j] represents the
# j^th query where you must find the answer for C_j / D_j = ?.
#
# Return the answers to all queries. If a single answer cannot be determined,
# return -1.0.
#
# Note: The input is always valid. You may assume that evaluating the queries
# will not result in division by zero and that there is no contradiction.
#
# Note: The variables that do not occur in the list of equations are undefined,
# so the answer cannot be determined for them.
#
# Example 1:
#
# Input: equations = [["a","b"],["b","c"]], values = [2.0,3.0], queries =
# [["a","c"],["b","a"],["a","e"],["a","a"],["x","x"]]
# Output: [6.00000,0.50000,-1.00000,1.00000,-1.00000]
# Explanation:
# Given: a / b = 2.0, b / c = 3.0
# queries are: a / c = ?, b / a = ?, a / e = ?, a / a = ?, x / x = ?
# return: [6.0, 0.5, -1.0, 1.0, -1.0 ]
# note: x is undefined => -1.0
#
# Example 2:
#
# Input: equations = [["a","b"],["b","c"],["bc","cd"]], values = [1.5,2.5,5.0],
# queries = [["a","c"],["c","b"],["bc","cd"],["cd","bc"]]
# Output: [3.75000,0.40000,5.00000,0.20000]
#
# Example 3:
#
# Input: equations = [["a","b"]], values = [0.5], queries =
# [["a","b"],["b","a"],["a","c"],["x","y"]]
# Output: [0.50000,2.00000,-1.00000,-1.00000]
#
# Constraints:
#
# 1 <= equations.length <= 20
#
# equations[i].length == 2
#
# 1 <= A_i.length, B_i.length <= 5
#
# values.length == equations.length
#
# 0.0 < values[i] <= 20.0
#
# 1 <= queries.length <= 20
#
# queries[i].length == 2
#
# 1 <= C_j.length, D_j.length <= 5
#
# A_i, B_i, C_j, D_j consist of lower case English letters and digits.
#

# @lc code=start
from collections import defaultdict, deque
from typing import Dict, List, Tuple


class Solution:
    def calcEquation(
        self,
        equations: List[List[str]],
        values: List[float],
        queries: List[List[str]],
    ) -> List[float]:
        """
        Interview explanation:
        Primary: weighted Union-Find. Each edge a/b=v means a = v*b relative
        to a component root. parent[x], weight[x] with x = weight[x]*parent[x].
        Query a/b = weight[a]/weight[b] if same root.

        Algorithm:
        - union(a,b,v): link roots with ratio so a/b=v holds.
        - find path-compresses and multiplies weights.
        - query: -1 if unknown or different components else wa/wb.

        Complexity: nearly O(E + Q) with path compression.
        """
        parent: Dict[str, str] = {}
        weight: Dict[str, float] = {}

        def find(x: str) -> Tuple[str, float]:
            if parent[x] != x:
                root, w = find(parent[x])
                weight[x] *= w
                parent[x] = root
            return parent[x], weight[x]

        def union(a: str, b: str, val: float) -> None:
            if a not in parent:
                parent[a] = a
                weight[a] = 1.0
            if b not in parent:
                parent[b] = b
                weight[b] = 1.0
            ra, wa = find(a)
            rb, wb = find(b)
            if ra != rb:
                parent[ra] = rb
                # a = wa * ra, b = wb * rb, a = val * b
                # wa * ra = val * wb * rb => ra = (val*wb/wa) * rb
                weight[ra] = val * wb / wa

        for (a, b), val in zip(equations, values):
            union(a, b, val)

        ans = []
        for a, b in queries:
            if a not in parent or b not in parent:
                ans.append(-1.0)
                continue
            ra, wa = find(a)
            rb, wb = find(b)
            if ra != rb:
                ans.append(-1.0)
            else:
                ans.append(wa / wb)
        return ans

    def calcEquationDFS(
        self,
        equations: List[List[str]],
        values: List[float],
        queries: List[List[str]],
    ) -> List[float]:
        """
        Interview explanation:
        Alternate: build bidirectional weighted graph (a→b:v, b→a:1/v),
        BFS/DFS product along path for each query.

        Complexity: O((E+V)*Q) time, O(E) space.
        """
        graph = defaultdict(list)
        for (a, b), val in zip(equations, values):
            graph[a].append((b, val))
            graph[b].append((a, 1.0 / val))

        def bfs(src: str, dst: str) -> float:
            if src not in graph or dst not in graph:
                return -1.0
            if src == dst:
                return 1.0
            q = deque([(src, 1.0)])
            seen = {src}
            while q:
                node, prod = q.popleft()
                for nei, w in graph[node]:
                    if nei in seen:
                        continue
                    nxt = prod * w
                    if nei == dst:
                        return nxt
                    seen.add(nei)
                    q.append((nei, nxt))
            return -1.0

        return [bfs(a, b) for a, b in queries]
# @lc code=end
