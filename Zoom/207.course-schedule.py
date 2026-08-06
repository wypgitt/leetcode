"""
Approach: Kahn's topological sort to detect cycles.
Data structure: adjacency lists store outgoing edges and an indegree array counts prerequisites remaining for each course.
Interview logic: courses with indegree zero can be taken now. Removing them decreases indegrees of dependent courses. If all courses are removed, no cycle exists.
Complexity: O(V + E) time and space.
Tests and edge cases: no prerequisites returns True; self-cycle returns False; disconnected course groups are handled by the initial zero-indegree queue.
"""
from __future__ import annotations
from collections import deque
from typing import List

# @lc code=start
from collections import deque
class Solution:
    def canFinish(self, numCourses: int, prerequisites: List[List[int]]) -> bool:
        graph = [[] for _ in range(numCourses)]
        indegree = [0] * numCourses
        for course, pre in prerequisites:
            graph[pre].append(course)
            indegree[course] += 1
        q = deque(i for i, deg in enumerate(indegree) if deg == 0)
        taken = 0
        while q:
            node = q.popleft()
            taken += 1
            for nxt in graph[node]:
                indegree[nxt] -= 1
                if indegree[nxt] == 0:
                    q.append(nxt)
        return taken == numCourses
# @lc code=end
