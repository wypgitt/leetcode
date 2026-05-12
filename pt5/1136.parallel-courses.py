from __future__ import annotations

from collections import deque
from typing import Deque, List


class Solution:
    def minimumSemesters(self, n: int, relations: List[List[int]]) -> int:
        graph = [[] for _ in range(n + 1)]
        indegree = [0] * (n + 1)

        for before, after in relations:
            graph[before].append(after)
            indegree[after] += 1

        queue: Deque[int] = deque(course for course in range(1, n + 1) if indegree[course] == 0)
        taken = 0
        semesters = 0

        while queue:
            semesters += 1
            for _ in range(len(queue)):
                course = queue.popleft()
                taken += 1
                for next_course in graph[course]:
                    indegree[next_course] -= 1
                    if indegree[next_course] == 0:
                        queue.append(next_course)

        return semesters if taken == n else -1

