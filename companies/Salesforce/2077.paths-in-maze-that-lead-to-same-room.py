#
# @lc app=leetcode id=2077 lang=python3
#
# [2077] Paths in Maze That Lead to Same Room
#
# https://leetcode.com/problems/paths-in-maze-that-lead-to-same-room/description/
#
# algorithms
# Medium (56.82%)
# Likes:    144
# Dislikes: 12
# Total Accepted:    6.7K
# Total Submissions: 11.8K
# Testcase Example:  "5\n[[1,2],[5,2],[4,1],[2,4],[3,1],[3,4]]"
#
#
# A maze consists of n rooms numbered from 1 to n, and some rooms are
# connected by corridors. You are given a 2D integer array corridors where
# corridors[i] = [room1_i, room2_i] indicates that there is a corridor
# connecting room1_i and room2_i, allowing a person in the maze to go from
# room1_i to room2_i and vice versa.
#
# The designer of the maze wants to know how confusing the maze is. The
# confusion score of the maze is the number of different cycles of length
# 3.
#
# For example, 1 → 2 → 3 → 1 is a cycle of length 3, but 1 → 2 → 3 → 4 and
# 1 → 2 → 3 → 2 → 1 are not.
#
# Two cycles are considered to be different if one or more of the rooms
# visited in the first cycle is not in the second cycle.
#
# Return the confusion score of the maze.
#
# Example 1:
#
# Input: n = 5, corridors = [[1,2],[5,2],[4,1],[2,4],[3,1],[3,4]]
# Output: 2
# Explanation:
# One cycle of length 3 is 4 → 1 → 3 → 4, denoted in red.
# Note that this is the same cycle as 3 → 4 → 1 → 3 or 1 → 3 → 4 → 1
# because the rooms are the same.
# Another cycle of length 3 is 1 → 2 → 4 → 1, denoted in blue.
# Thus, there are two different cycles of length 3.
#
# Example 2:
#
# Input: n = 4, corridors = [[1,2],[3,4]]
# Output: 0
# Explanation:
# There are no cycles of length 3.
#
# Constraints:
#
# 2 <= n <= 1000
#
# 1 <= corridors.length <= 5 * 10^4
#
# corridors[i].length == 2
#
# 1 <= room1_i, room2_i <= n
#
# room1_i != room2_i
#
# There are no duplicate corridors.
#
# @lc code=start
from typing import List
from collections import defaultdict


class Solution:
    def numberOfPaths(self, n: int, corridors: List[List[int]]) -> int:
        """
        Interview explanation:
        Premium. Undirected graph of n rooms and corridors. Count length-2 cycles
        (triangles): distinct rooms a-b-c-a forming a cycle of 3 edges.

        Algorithm:
        - Build adjacency sets; for each edge (u,v), count common neighbors.

        Complexity: O(n + m * deg) ~ O(n^2) worst; fine for typical constraints.
        """
        g = defaultdict(set)
        for a, b in corridors:
            if a > b:
                a, b = b, a
            g[a].add(b)
            g[b].add(a)
        ans = 0
        for a, b in corridors:
            ans += len(g[a] & g[b])
        return ans // 3

    def numberOfPaths_enum(self, n: int, corridors: List[List[int]]) -> int:
        """
        Interview explanation:
        Alternate: for each node, enumerate pairs of neighbors that are connected.

        Algorithm:
        - For u, for each pair (v,w) of neighbors with v<w, if edge vw exists, +1.

        Complexity: O(sum deg(u)^2) time, O(n+m) space.
        """
        g = [set() for _ in range(n + 1)]
        for a, b in corridors:
            g[a].add(b)
            g[b].add(a)
        ans = 0
        for u in range(1, n + 1):
            nbrs = sorted(g[u])
            for i in range(len(nbrs)):
                for j in range(i + 1, len(nbrs)):
                    if nbrs[j] in g[nbrs[i]]:
                        ans += 1
        return ans // 3
# @lc code=end
