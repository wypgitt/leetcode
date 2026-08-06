#
# @lc app=leetcode id=3607 lang=python3
#
# [3607] Power Grid Maintenance
#
# https://leetcode.com/problems/power-grid-maintenance/description/
#
# algorithms
# Medium (56.14%)
# Likes:    547
# Dislikes: 59
# Total Accepted:    94.8K
# Total Submissions: 168.9K
# Testcase Example:  "5\n[[1,2],[2,3],[3,4],[4,5]]\n[[1,3],[2,1],[1,1],[2,2],[1,2]]"
#
#
# You are given an integer c representing c power stations, each with a
# unique identifier id from 1 to c (1‑based indexing).
#
# These stations are interconnected via n bidirectional cables,
# represented by a 2D array connections, where each element connections[i]
# = [u_i, v_i] indicates a connection between station u_i and station v_i.
# Stations that are directly or indirectly connected form a power grid.
#
# Initially, all stations are online (operational).
#
# You are also given a 2D array queries, where each query is one of the
# following two types:
#
# [1, x]: A maintenance check is requested for station x. If station x is
# online, it resolves the check by itself. If station x is offline, the
# check is resolved by the operational station with the smallest id in the
# same power grid as x. If no operational station exists in that grid,
# return -1.
#
# [2, x]: Station x goes offline (i.e., it becomes non-operational).
#
# Return an array of integers representing the results of each query of
# type [1, x] in the order they appear.
#
# Note: The power grid preserves its structure; an offline
# (non‑operational) node remains part of its grid and taking it offline
# does not alter connectivity.
#
# Example 1:
#
# Input: c = 5, connections = [[1,2],[2,3],[3,4],[4,5]], queries =
# [[1,3],[2,1],[1,1],[2,2],[1,2]]
#
# Output: [3,2,3]
#
# Explanation:
#
# Initially, all stations {1, 2, 3, 4, 5} are online and form a single
# power grid.
#
# Query [1,3]: Station 3 is online, so the maintenance check is resolved
# by station 3.
#
# Query [2,1]: Station 1 goes offline. The remaining online stations are
# {2, 3, 4, 5}.
#
# Query [1,1]: Station 1 is offline, so the check is resolved by the
# operational station with the smallest id among {2, 3, 4, 5}, which is
# station 2.
#
# Query [2,2]: Station 2 goes offline. The remaining online stations are
# {3, 4, 5}.
#
# Query [1,2]: Station 2 is offline, so the check is resolved by the
# operational station with the smallest id among {3, 4, 5}, which is
# station 3.
#
# Example 2:
#
# Input: c = 3, connections = [], queries = [[1,1],[2,1],[1,1]]
#
# Output: [1,-1]
#
# Explanation:
#
# There are no connections, so each station is its own isolated grid.
#
# Query [1,1]: Station 1 is online in its isolated grid, so the
# maintenance check is resolved by station 1.
#
# Query [2,1]: Station 1 goes offline.
#
# Query [1,1]: Station 1 is offline and there are no other stations in its
# grid, so the result is -1.
#
# Constraints:
#
# 1 <= c <= 10^5
#
# 0 <= n == connections.length <= min(10^5, c * (c - 1) / 2)
#
# connections[i].length == 2
#
# 1 <= u_i, v_i <= c
#
# u_i != v_i
#
# 1 <= queries.length <= 2 * 10^5
#
# queries[i].length == 2
#
# queries[i][0] is either 1 or 2.
#
# 1 <= queries[i][1] <= c
#

# @lc code=start

from typing import List


class Solution:
    def processQueries(
        self, c: int, connections: List[List[int]], queries: List[List[int]]
    ) -> List[int]:
        """
        Interview explanation:
        Grids are connectivity components. Type-1: if x online return x, else
        smallest online id in x's component (-1 if none). Type-2: take x offline.

        Algorithm:
        - DFS/flood-fill components; store each component's stations sorted
          descending so the back is the current smallest candidate.
        - Lazy-pop offline ids from the component list on queries.

        Complexity: O(c + E + Q) time, O(c + E) space.
        """
        adj: List[List[int]] = [[] for _ in range(c)]
        for u, v in connections:
            adj[u - 1].append(v - 1)
            adj[v - 1].append(u - 1)

        comp = [-1] * c

        def dfs(start: int) -> None:
            stack = [start]
            while stack:
                u = stack.pop()
                if comp[u] != -1:
                    continue
                comp[u] = start
                for v in adj[u]:
                    if comp[v] == -1:
                        stack.append(v)

        for i in range(c):
            if comp[i] == -1:
                dfs(i)

        groups: List[List[int]] = [[] for _ in range(c)]
        for i in range(c - 1, -1, -1):
            groups[comp[i]].append(i)

        online = [True] * c
        ans: List[int] = []
        for t, x in queries:
            x -= 1
            if t == 1:
                if online[x]:
                    ans.append(x + 1)
                else:
                    g = groups[comp[x]]
                    while g and not online[g[-1]]:
                        g.pop()
                    ans.append(g[-1] + 1 if g else -1)
            else:
                online[x] = False
        return ans
# @lc code=end
