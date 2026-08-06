#
# @lc app=leetcode id=2307 lang=python3
#
# [2307] Check for Contradictions in Equations
#
# https://leetcode.com/problems/check-for-contradictions-in-equations/description/
#
# algorithms
# Hard (44.05%)
# Likes:    70
# Dislikes: 27
# Total Accepted:    5.4K
# Total Submissions: 12.2K
# Testcase Example:  "[[\"a\",\"b\"],[\"b\",\"c\"],[\"a\",\"c\"]]\n[3,0.5,1.5]"
#
#
# You are given a 2D array of strings equations and an array of real
# numbers values, where equations[i] = [A_i, B_i] and values[i] means that
# A_i / B_i = values[i].
#
# Determine if there exists a contradiction in the equations. Return true
# if there is a contradiction, or false otherwise.
#
# Note:
#
# When checking if two numbers are equal, check that their absolute
# difference is less than 10^-5.
#
# The testcases are generated such that there are no cases targeting
# precision, i.e. using double is enough to solve the problem.
#
# Example 1:
#
# Input: equations = [["a","b"],["b","c"],["a","c"]], values = [3,0.5,1.5]
# Output: false
# Explanation:
# The given equations are: a / b = 3, b / c = 0.5, a / c = 1.5
# There are no contradictions in the equations. One possible assignment to
# satisfy all equations is:
# a = 3, b = 1 and c = 2.
#
# Example 2:
#
# Input: equations = [["le","et"],["le","code"],["code","et"]], values =
# [2,5,0.5]
# Output: true
# Explanation:
# The given equations are: le / et = 2, le / code = 5, code / et = 0.5
# Based on the first two equations, we get code / et = 0.4.
# Since the third equation is code / et = 0.5, we get a contradiction.
#
# Constraints:
#
# 1 <= equations.length <= 100
#
# equations[i].length == 2
#
# 1 <= A_i.length, B_i.length <= 5
#
# A_i, B_i consist of lowercase English letters.
#
# equations.length == values.length
#
# 0.0 < values[i] <= 10.0
#
# values[i] has a maximum of 2 decimal places.
#
# @lc code=start
from typing import List
from collections import defaultdict


class Solution:
    def checkContradictions(self, equations: List[List[str]], values: List[float]) -> bool:
        """
        Interview explanation:
        Equations Ai/Bi = values[i]. Detect whether the system is contradictory
        (inconsistent ratio constraints), with float eps 1e-5.

        Algorithm:
        - Weighted Union-Find with weight[x] = root/x after find.
        - On a/b = v: if same root, check v*weight[a] ≈ weight[b]; else union.

        Complexity: O(n α(n)) time, O(n) space.
        """
        idx = {}
        for a, b in equations:
            if a not in idx:
                idx[a] = len(idx)
            if b not in idx:
                idx[b] = len(idx)
        n = len(idx)
        parent = list(range(n))
        weight = [1.0] * n
        eps = 1e-5

        def find(x: int) -> int:
            if parent[x] != x:
                r = find(parent[x])
                weight[x] *= weight[parent[x]]
                parent[x] = r
            return parent[x]

        for (a, b), v in zip(equations, values):
            ia, ib = idx[a], idx[b]
            pa, pb = find(ia), find(ib)
            if pa != pb:
                parent[pb] = pa
                weight[pb] = v * weight[ia] / weight[ib]
            elif abs(v * weight[ia] - weight[ib]) >= eps:
                return True
        return False

    def checkContradictions_uf(self, equations: List[List[str]], values: List[float]) -> bool:
        """
        Interview explanation:
        Classic weighted UF approach (same as primary).

        Algorithm:
        - Maintain ratios to roots; detect inconsistent edges.

        Complexity: O(n α(n)) time, O(n) space.
        """
        return self.checkContradictions(equations, values)

    def checkContradictions_dfs(self, equations: List[List[str]], values: List[float]) -> bool:
        """
        Interview explanation:
        Alternate graph DFS: edge u->v with weight w means u/v = w; assign
        absolute values per component and detect conflicts.

        Algorithm:
        - Build bidirectional graph; DFS assign values; conflict if mismatch.

        Complexity: O(n + m) time, O(n + m) space.
        """
        g = defaultdict(list)
        for (a, b), v in zip(equations, values):
            g[a].append((b, v))
            g[b].append((a, 1.0 / v))
        val = {}
        eps = 1e-5

        def dfs(u: str) -> bool:
            for v, w in g[u]:
                expect = val[u] / w  # u/v = w => v = u/w
                if v in val:
                    if abs(val[v] - expect) >= eps:
                        return False
                else:
                    val[v] = expect
                    if not dfs(v):
                        return False
            return True

        for node in list(g.keys()):
            if node not in val:
                val[node] = 1.0
                if not dfs(node):
                    return True
        return False
# @lc code=end
