"""
Approach: Kahn's topological sort and return the produced order.
Data structure: adjacency lists plus indegree counts model the prerequisite graph.
Interview logic: a course can be output only when all prerequisites have been output. If a cycle exists, some courses never reach indegree zero, so return an empty list.
Complexity: O(V + E) time and space.
Tests and edge cases: multiple valid orders are acceptable; no prerequisites can return 0..n-1; cycles return [].
"""
from __future__ import annotations
from collections import deque
from typing import List

# @lc code=start
from collections import deque
class Solution:
    def findOrder(self, numCourses: int, prerequisites: List[List[int]]) -> List[int]:
        graph = [[] for _ in range(numCourses)]
        indegree = [0] * numCourses
        for course, pre in prerequisites:
            graph[pre].append(course)
            indegree[course] += 1
        q = deque(i for i, deg in enumerate(indegree) if deg == 0)
        order = []
        while q:
            node = q.popleft()
            order.append(node)
            for nxt in graph[node]:
                indegree[nxt] -= 1
                if indegree[nxt] == 0:
                    q.append(nxt)
        return order if len(order) == numCourses else []
# @lc code=end
