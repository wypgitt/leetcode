#
# @lc app=leetcode id=3383 lang=python3
#
# [3383] Minimum Runes to Add to Cast Spell
#
# https://leetcode.com/problems/minimum-runes-to-add-to-cast-spell/description/
#
# algorithms
# Hard (44.87%)
# Likes:    9
# Dislikes: 2
# Total Accepted:    865
# Total Submissions: 1.9K
# Testcase Example:  "6\n[0]\n[0,1,2,3]\n[1,2,3,0]"
#
#
# Alice has just graduated from wizard school, and wishes to cast a magic
# spell to celebrate. The magic spell contains certain focus points where
# magic needs to be concentrated, and some of these focus points contain
# magic crystals which serve as the spell's energy source. Focus points
# can be linked through directed runes, which channel magic flow from one
# focus point to another.
#
# You are given a integer n denoting the number of focus points and an
# array of integers crystals where crystals[i] indicates a focus point
# which holds a magic crystal. You are also given two integer arrays
# flowFrom and flowTo, which represent the existing directed runes. The
# i^th rune allows magic to freely flow from focus point flowFrom[i] to
# focus point flowTo[i].
#
# You need to find the number of directed runes Alice must add to her
# spell, such that each focus point either:
#
# Contains a magic crystal.
#
# Receives magic flow from another focus point.
#
# Return the minimum number of directed runes that she should add.
#
# Example 1:
#
# Input: n = 6, crystals = [0], flowFrom = [0,1,2,3], flowTo = [1,2,3,0]
#
# Output: 2
#
# Explanation:
#
# Add two directed runes:
#
# From focus point 0 to focus point 4.
#
# From focus point 0 to focus point 5.
#
# Example 2:
#
# Input: n = 7, crystals = [3,5], flowFrom = [0,1,2,3,5], flowTo =
# [1,2,0,4,6]
#
# Output: 1
#
# Explanation:
#
# Add a directed rune from focus point 4 to focus point 2.
#
# Constraints:
#
# 2 <= n <= 10^5
#
# 1 <= crystals.length <= n
#
# 0 <= crystals[i] <= n - 1
#
# 1 <= flowFrom.length == flowTo.length <= min(2 * 10^5, (n * (n - 1)) /
# 2)
#
# 0 <= flowFrom[i], flowTo[i] <= n - 1
#
# flowFrom[i] != flowTo[i]
#
# All pre-existing directed runes are distinct.
#

# @lc code=start

from typing import List


class Solution:
    def minRunesToAdd(
        self, n: int, crystals: List[int], flowFrom: List[int], flowTo: List[int]
    ) -> int:
        """
        Interview explanation:
        Magic reaches a node if it has a crystal or positive in-degree. Within an
        SCC every node already has internal in-degree when |SCC|>1 (or a loop).
        Condensation sources without a crystal each need one incoming rune.

        Algorithm:
        - Kosaraju SCC (iterative) on the directed flow graph.
        - Mark SCCs that contain a crystal or have an edge from another SCC.
        - Answer = number of unmarked SCCs (sources that still need a rune).

        Complexity: O(n + m) time, O(n + m) space.
        """
        g = [[] for _ in range(n)]
        rg = [[] for _ in range(n)]
        for u, v in zip(flowFrom, flowTo):
            g[u].append(v)
            rg[v].append(u)

        order: List[int] = []
        seen = [False] * n
        for s in range(n):
            if seen[s]:
                continue
            stack = [s]
            seen[s] = True
            while stack:
                u = stack[-1]
                advanced = False
                for v in g[u]:
                    if not seen[v]:
                        seen[v] = True
                        stack.append(v)
                        advanced = True
                        break
                if not advanced:
                    order.append(stack.pop())

        comp = [-1] * n
        cid = 0
        for s in reversed(order):
            if comp[s] != -1:
                continue
            stack = [s]
            comp[s] = cid
            while stack:
                u = stack.pop()
                for v in rg[u]:
                    if comp[v] == -1:
                        comp[v] = cid
                        stack.append(v)
            cid += 1

        has_in = [False] * cid
        has_crystal = [False] * cid
        for u, v in zip(flowFrom, flowTo):
            if comp[u] != comp[v]:
                has_in[comp[v]] = True
        for c in crystals:
            has_crystal[comp[c]] = True

        return sum(1 for i in range(cid) if not has_in[i] and not has_crystal[i])
# @lc code=end
