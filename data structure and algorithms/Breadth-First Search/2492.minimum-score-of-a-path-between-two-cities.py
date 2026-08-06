#
# @lc app=leetcode id=2492 lang=python3
#
# [2492] Minimum Score of a Path Between Two Cities
#
# https://leetcode.com/problems/minimum-score-of-a-path-between-two-cities/description/
#
# algorithms
# Medium (66.24%)
# Likes:    2133
# Dislikes: 328
# Total Accepted:    206.5K
# Total Submissions: 311.8K
# Testcase Example:  "4\n[[1,2,9],[2,3,6],[2,4,5],[1,4,7]]"
#
# You are given a positive integer n representing n cities numbered from 1 to n.
# You are also given a 2D array roads where roads[i] = [a_i, b_i, distance_i]
# indicates that there is a bidirectional road between cities a_i and b_i with a
# distance equal to distance_i. The cities graph is not necessarily connected.
#
# The score of a path between two cities is defined as the minimum distance of a
# road in this path.
#
# Return the minimum possible score of a path between cities 1 and n.
#
# Note:
#
#
# A path is a sequence of roads between two cities.
#
#
# It is allowed for a path to contain the same road multiple times, and you can
# visit cities 1 and n multiple times along the path.
#
#
# The test cases are generated such that there is at least one path between 1
# and n.
#
#
#
# Example 1:
#
# Input: n = 4, roads = [[1,2,9],[2,3,6],[2,4,5],[1,4,7]]
# Output: 5
# Explanation: The path from city 1 to 4 with the minimum score is: 1 -> 2 -> 4.
# The score of this path is min(9,5) = 5.
# It can be shown that no other path has less score.
#
# Example 2:
#
# Input: n = 4, roads = [[1,2,2],[1,3,4],[3,4,7]]
# Output: 2
# Explanation: The path from city 1 to 4 with the minimum score is: 1 -> 2 -> 1
# -> 3 -> 4. The score of this path is min(2,2,4,7) = 2.
#
#
#
# Constraints:
#
#
# 2 <= n <= 10^5
#
#
# 1 <= roads.length <= 10^5
#
#
# roads[i].length == 3
#
#
# 1 <= a_i, b_i <= n
#
#
# a_i != b_i
#
#
# 1 <= distance_i <= 10^4
#
#
# There are no repeated edges.
#
#
# There is at least one path between 1 and n.
#

# @lc code=start
from typing import List
from collections import defaultdict, deque


class Solution:
    def minScore(self, n: int, roads: List[List[int]]) -> int:
        """
        Interview explanation:
        Undirected graph; path from 1 to n may use any roads in the connected
        component. Score of a path is min edge; minimize score over paths =
        min edge in component of 1 (same as n).

        Algorithm:
        - BFS/DFS/UF from 1; track minimum edge weight seen in component.

        Complexity: O(n+m) time, O(n+m) space.
        """
        g = defaultdict(list)
        for a, b, d in roads:
            g[a].append((b, d))
            g[b].append((a, d))
        vis = [False] * (n + 1)
        q = deque([1])
        vis[1] = True
        ans = 10**9
        while q:
            u = q.popleft()
            for v, d in g[u]:
                ans = min(ans, d)
                if not vis[v]:
                    vis[v] = True
                    q.append(v)
        return ans

    def minScore_uf(self, n: int, roads: List[List[int]]) -> int:
        """
        Interview explanation:
        Alternate Union-Find: min edge among edges connecting nodes in 1's
        component.

        Algorithm:
        - Union all; scan edges with find(a)==find(1).

        Complexity: O(m α(n)) time, O(n) space.
        """
        parent = list(range(n + 1))

        def find(x: int) -> int:
            while parent[x] != x:
                parent[x] = parent[parent[x]]
                x = parent[x]
            return x

        def union(a: int, b: int) -> None:
            ra, rb = find(a), find(b)
            if ra != rb:
                parent[rb] = ra

        for a, b, _ in roads:
            union(a, b)
        root = find(1)
        return min(d for a, b, d in roads if find(a) == root)
# @lc code=end

