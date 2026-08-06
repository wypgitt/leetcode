#
# @lc app=leetcode id=1466 lang=python3
#
# [1466] Reorder Routes to Make All Paths Lead to the City Zero
#
# https://leetcode.com/problems/reorder-routes-to-make-all-paths-lead-to-the-city-zero/description/
#
# algorithms
# Medium (66.05%)
# Likes:    4697
# Dislikes: 152
# Total Accepted:    333K
# Total Submissions: 504K
# Testcase Example:  "6"
#
# There are n cities numbered from 0 to n - 1 and n - 1 roads such that there
# is only one way to travel between two different cities (this network form a
# tree). Last year, The ministry of transport decided to orient the roads in
# one direction because they are too narrow.
#
# Roads are represented by connections where connections[i] = [a_i, b_i]
# represents a road from city a_i to city b_i.
#
# This year, there will be a big event in the capital (city 0), and many people
# want to travel to this city.
#
# Your task consists of reorienting some roads such that each city can visit
# the city 0. Return the minimum number of edges changed.
#
# It's guaranteed that each city can reach city 0 after reorder.
#
# Example 1:
#
# Input: n = 6, connections = [[0,1],[1,3],[2,3],[4,0],[4,5]]
# Output: 3
# Explanation: Change the direction of edges show in red such that each node
# can reach the node 0 (capital).
#
# Example 2:
#
# Input: n = 5, connections = [[1,0],[1,2],[3,2],[3,4]]
# Output: 2
# Explanation: Change the direction of edges show in red such that each node
# can reach the node 0 (capital).
#
# Example 3:
#
# Input: n = 3, connections = [[1,0],[2,0]]
# Output: 0
#
# Constraints:
#
# 2 <= n <= 5 * 10^4
#
# connections.length == n - 1
#
# connections[i].length == 2
#
# 0 <= a_i, b_i <= n - 1
#
# a_i != b_i
#

# @lc code=start
from typing import List
from collections import defaultdict, deque


class Solution:
    def minReorder(self, n: int, connections: List[List[int]]) -> int:
        """
        Interview explanation:
        Tree rooted conceptually at 0; edges are directed. Count edges that
        point away from 0 when traversing outward — those must be reversed.

        Algorithm:
        - Build undirected adj with sign: +1 if original a→b, 0 if reverse
          stored. DFS/BFS from 0; add edge cost when traversing original direction.

        Complexity: O(n) time/space.
        """
        adj = defaultdict(list)
        for a, b in connections:
            adj[a].append((b, 1))
            adj[b].append((a, 0))
        ans = 0
        seen = {0}
        stack = [0]
        while stack:
            u = stack.pop()
            for v, need in adj[u]:
                if v not in seen:
                    ans += need
                    seen.add(v)
                    stack.append(v)
        return ans

    def minReorder_bfs(self, n: int, connections: List[List[int]]) -> int:
        """
        Interview explanation:
        Alternate: BFS from 0 with the same signed adjacency.

        Algorithm:
        - Queue BFS; accumulate reorder count on forward edges.

        Complexity: O(n) time/space.
        """
        adj = defaultdict(list)
        for a, b in connections:
            adj[a].append((b, 1))
            adj[b].append((a, 0))
        ans = 0
        q = deque([0])
        seen = {0}
        while q:
            u = q.popleft()
            for v, need in adj[u]:
                if v not in seen:
                    ans += need
                    seen.add(v)
                    q.append(v)
        return ans
# @lc code=end
