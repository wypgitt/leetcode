from __future__ import annotations

from collections import defaultdict, deque
from typing import DefaultDict, Deque, List, Tuple


class Solution:
    def shortestAlternatingPaths(
        self, n: int, redEdges: List[List[int]], blueEdges: List[List[int]]
    ) -> List[int]:
        graph: List[DefaultDict[int, List[int]]] = [defaultdict(list), defaultdict(list)]
        for u, v in redEdges:
            graph[0][u].append(v)
        for u, v in blueEdges:
            graph[1][u].append(v)

        answer = [-1] * n
        visited = [[False, False] for _ in range(n)]
        queue: Deque[Tuple[int, int, int]] = deque([(0, 0, 0), (0, 1, 0)])
        visited[0][0] = visited[0][1] = True

        while queue:
            node, last_color, distance = queue.popleft()
            if answer[node] == -1:
                answer[node] = distance

            next_color = 1 - last_color
            for neighbor in graph[next_color][node]:
                if not visited[neighbor][next_color]:
                    visited[neighbor][next_color] = True
                    queue.append((neighbor, next_color, distance + 1))

        return answer

