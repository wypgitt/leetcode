#
# @lc app=leetcode id=1245 lang=python3
#
# [1245] Tree Diameter
#
# https://leetcode.com/problems/tree-diameter/description/
#
# algorithms
# Medium (61.25%)
# Likes:    904
# Dislikes: 26
# Total Accepted:    56.7K
# Total Submissions: 92.5K
# Testcase Example:  '[[0,1],[0,2]]'
#
# The diameter of a tree is the number of edges in the longest path in that
# tree.
# 
# There is an undirected tree of n nodes labeled from 0 to n - 1. You are given
# a 2D array edges where edges.length == n - 1 and edges[i] = [ai, bi]
# indicates that there is an undirected edge between nodes ai and bi in the
# tree.
# 
# Return the diameter of the tree.
# 
# 
# Example 1:
# 
# 
# Input: edges = [[0,1],[0,2]]
# Output: 2
# Explanation: The longest path of the tree is the path 1 - 0 - 2.
# 
# 
# Example 2:
# 
# 
# Input: edges = [[0,1],[1,2],[2,3],[1,4],[4,5]]
# Output: 4
# Explanation: The longest path of the tree is the path 3 - 2 - 1 - 4 - 5.
# 
# 
# 
# Constraints:
# 
# 
# n == edges.length + 1
# 1 <= n <= 10^4
# 0 <= ai, bi < n
# ai != bi
# 
# 
#

# @lc code=start
from collections import defaultdict, deque
from typing import List


class Solution:
    def treeDiameter(self, edges: List[List[int]]) -> int:
        if not edges:
            return 0

        graph = defaultdict(list)
        for a, b in edges:
            graph[a].append(b)
            graph[b].append(a)

        def farthest(start: int) -> tuple[int, int]:
            queue = deque([(start, -1, 0)])
            far_node = start
            far_dist = 0

            while queue:
                node, parent, dist = queue.popleft()
                if dist > far_dist:
                    far_node = node
                    far_dist = dist
                for nei in graph[node]:
                    if nei != parent:
                        queue.append((nei, node, dist + 1))

            return far_node, far_dist

        end, _ = farthest(edges[0][0])
        _, diameter = farthest(end)
        return diameter
# @lc code=end

# Explanation
# -----------
# In any tree, if we start from an arbitrary node and find the farthest node A,
# then one endpoint of the diameter is A. Running BFS/DFS again from A gives
# the diameter length. This works because tree paths are unique.
#
# The adjacency list is the right representation for an undirected tree. BFS
# tracks (node, parent, distance), so no visited set is required beyond the
# parent in a tree.
#
# Edge cases: a single-node tree has no edges and diameter 0; a chain returns
# n - 1; a star returns 2.
#
# Time complexity: O(n), two full traversals.
# Space complexity: O(n) for the graph and BFS queue.
