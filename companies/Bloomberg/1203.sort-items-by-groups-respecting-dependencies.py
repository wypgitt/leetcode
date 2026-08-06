#
# @lc app=leetcode id=1203 lang=python3
#
# [1203] Sort Items by Groups Respecting Dependencies
#
# https://leetcode.com/problems/sort-items-by-groups-respecting-dependencies/description/
#
# algorithms
# Hard (66.02%)
# Likes:    1932
# Dislikes: 323
# Total Accepted:    69.5K
# Total Submissions: 105K
# Testcase Example:  "8"
#
# There are n items each belonging to zero or one of m groups where group[i] is
# the group that the i-th item belongs to and it's equal to -1 if the i-th item
# belongs to no group. The items and the groups are zero indexed. A group can
# have no item belonging to it.
#
# Return a sorted list of the items such that:
#
# The items that belong to the same group are next to each other in the sorted
# list.
#
# There are some relations between these items where beforeItems[i] is a list
# containing all the items that should come before the i-th item in the sorted
# array (to the left of the i-th item).
#
# Return any solution if there is more than one solution and return an empty
# list if there is no solution.
#
# Example 1:
#
# Input: n = 8, m = 2, group = [-1,-1,1,0,0,1,0,-1], beforeItems =
# [[],[6],[5],[6],[3,6],[],[],[]]
# Output: [6,3,4,1,5,2,0,7]
#
# Example 2:
#
# Input: n = 8, m = 2, group = [-1,-1,1,0,0,1,0,-1], beforeItems =
# [[],[6],[5],[6],[3],[],[4],[]]
# Output: []
# Explanation: This is the same as example 1 except that 4 needs to be before 6
# in the sorted list.
#
# Constraints:
#
# 1 <= m <= n <= 3 * 10^4
#
# group.length == beforeItems.length == n
#
# -1 <= group[i] <= m - 1
#
# 0 <= beforeItems[i].length <= n - 1
#
# 0 <= beforeItems[i][j] <= n - 1
#
# i != beforeItems[i][j]
#
# beforeItems[i] does not contain duplicates elements.
#


# @lc code=start
from typing import List
from collections import defaultdict, deque

class Solution:
    def sortItems(self, n: int, m: int, group: List[int], beforeItems: List[List[int]]) -> List[int]:
        """
        Interview explanation:
        Items and groups both have precedence constraints. Assign each -1 group
        a unique new group id, then topological-sort groups and items within
        groups (Kahn). Edges between items induce group edges if groups differ.

        Algorithm:
        - Remap ungrouped items to new group ids
        - Build item graph + group graph from beforeItems
        - Topo sort groups, then topo sort items; emit by group order

        Complexity: O(n + e) time/space.
        """
        # Assign unique group to ungrouped items
        for i in range(n):
            if group[i] == -1:
                group[i] = m
                m += 1

        item_adj = [[] for _ in range(n)]
        item_indeg = [0] * n
        group_adj = [[] for _ in range(m)]
        group_indeg = [0] * m

        for v in range(n):
            for u in beforeItems[v]:
                item_adj[u].append(v)
                item_indeg[v] += 1
                gu, gv = group[u], group[v]
                if gu != gv:
                    group_adj[gu].append(gv)
                    group_indeg[gv] += 1

        def topo(nodes: List[int], adj, indeg) -> List[int]:
            deg = {x: indeg[x] for x in nodes}
            q = deque([x for x in nodes if deg[x] == 0])
            order = []
            while q:
                u = q.popleft()
                order.append(u)
                for v in adj[u]:
                    if v not in deg:
                        continue
                    deg[v] -= 1
                    if deg[v] == 0:
                        q.append(v)
            return order if len(order) == len(nodes) else []

        item_order = topo(list(range(n)), item_adj, item_indeg)
        if not item_order:
            return []
        group_order = topo(list(range(m)), group_adj, group_indeg)
        if not group_order:
            return []

        grouped = defaultdict(list)
        for item in item_order:
            grouped[group[item]].append(item)

        ans = []
        for g in group_order:
            ans.extend(grouped[g])
        return ans
# @lc code=end
