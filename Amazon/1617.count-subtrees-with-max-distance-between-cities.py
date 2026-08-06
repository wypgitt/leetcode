#
# @lc app=leetcode id=1617 lang=python3
#
# [1617] Count Subtrees With Max Distance Between Cities
#
# https://leetcode.com/problems/count-subtrees-with-max-distance-between-cities/description/
#
# algorithms
# Hard (67.42%)
# Likes:    580
# Dislikes: 44
# Total Accepted:    15.5K
# Total Submissions: 23.0K
# Testcase Example:  "4"
#
# There are n cities numbered from 1 to n. You are given an array edges of size
# n-1, where edges[i] = [u_i, v_i] represents a bidirectional edge between
# cities u_i and v_i. There exists a unique path between each pair of cities.
# In other words, the cities form a tree.
#
# A subtree is a subset of cities where every city is reachable from every
# other city in the subset, where the path between each pair passes through
# only the cities from the subset. Two subtrees are different if there is a
# city in one subtree that is not present in the other.
#
# For each d from 1 to n-1, find the number of subtrees in which the maximum
# distance between any two cities in the subtree is equal to d.
#
# Return an array of size n-1 where the d^th element (1-indexed) is the number
# of subtrees in which the maximum distance between any two cities is equal to
# d.
#
# Notice that the distance between the two cities is the number of edges in the
# path between them.
#
# Example 1:
#
# Input: n = 4, edges = [[1,2],[2,3],[2,4]]
# Output: [3,4,0]
# Explanation:
# The subtrees with subsets {1,2}, {2,3} and {2,4} have a max distance of 1.
# The subtrees with subsets {1,2,3}, {1,2,4}, {2,3,4} and {1,2,3,4} have a max
# distance of 2.
# No subtree has two nodes where the max distance between them is 3.
#
# Example 2:
#
# Input: n = 2, edges = [[1,2]]
# Output: [1]
#
# Example 3:
#
# Input: n = 3, edges = [[1,2],[2,3]]
# Output: [2,1]
#
# Constraints:
#
# 2 <= n <= 15
#
# edges.length == n-1
#
# edges[i].length == 2
#
# 1 <= u_i, v_i <= n
#
# All pairs (u_i, v_i) are distinct.
#

# @lc code=start
from typing import List
from collections import deque


class Solution:
    def countSubgraphsForEachDiameter(self, n: int, edges: List[List[int]]) -> List[int]:
        """
        Interview explanation:
        n<=15 cities. Enumerate connected subsets (bitmasks); for each compute
        diameter via BFS from all nodes in subset; tally by diameter.

        Algorithm (bitmask + BFS):
        - Build adj. For mask 1..(1<<n)-1: if |mask|>1 and connected, diameter =
          max eccentricity; ans[d-1]++.

        Complexity: O(2^n * n^2) time, O(n) space.
        """
        g = [[] for _ in range(n)]
        for u, v in edges:
            u -= 1
            v -= 1
            g[u].append(v)
            g[v].append(u)
        ans = [0] * (n - 1)

        def bfs(start: int, mask: int):
            q = deque([start])
            dist = {start: 0}
            while q:
                u = q.popleft()
                for v in g[u]:
                    if (mask >> v) & 1 and v not in dist:
                        dist[v] = dist[u] + 1
                        q.append(v)
            return dist

        for mask in range(1, 1 << n):
            nodes = [i for i in range(n) if mask >> i & 1]
            if len(nodes) < 2:
                continue
            dist0 = bfs(nodes[0], mask)
            if len(dist0) != len(nodes):
                continue
            # diameter: max over BFS distances from all nodes
            diam = 0
            for s in nodes:
                d = bfs(s, mask)
                diam = max(diam, max(d.values()))
            ans[diam - 1] += 1
        return ans

    def countSubgraphsForEachDiameter_floyd(self, n: int, edges: List[List[int]]) -> List[int]:
        """
        Interview explanation:
        Alternate: Floyd-Warshall all-pairs distances on tree; for each subset check
        connectivity (#edges in induced == |S|-1) and take max pairwise dist.

        Algorithm (Floyd + bitmask):
        - dist via FW; for each mask with >=2 nodes, verify tree edges count and
          compute max dist among pairs in mask.

        Complexity: O(n^3 + 2^n * n^2) time.
        """
        INF = 10**9
        dist = [[INF] * n for _ in range(n)]
        for i in range(n):
            dist[i][i] = 0
        for u, v in edges:
            u -= 1
            v -= 1
            dist[u][v] = dist[v][u] = 1
        for k in range(n):
            for i in range(n):
                for j in range(n):
                    if dist[i][j] > dist[i][k] + dist[k][j]:
                        dist[i][j] = dist[i][k] + dist[k][j]
        ans = [0] * (n - 1)
        for mask in range(1, 1 << n):
            nodes = [i for i in range(n) if mask >> i & 1]
            if len(nodes) < 2:
                continue
            edge_cnt = 0
            diam = 0
            ok = True
            for i in range(len(nodes)):
                for j in range(i + 1, len(nodes)):
                    d = dist[nodes[i]][nodes[j]]
                    if d >= INF:
                        ok = False
                        break
                    if d == 1:
                        edge_cnt += 1
                    diam = max(diam, d)
                if not ok:
                    break
            if ok and edge_cnt == len(nodes) - 1:
                ans[diam - 1] += 1
        return ans
# @lc code=end
