from __future__ import annotations

from typing import List


class Solution:
    def minimumCost(self, n: int, connections: List[List[int]]) -> int:
        if n == 1:
            return 0

        parent = list(range(n + 1))
        rank = [0] * (n + 1)

        def find(x: int) -> int:
            while parent[x] != x:
                parent[x] = parent[parent[x]]
                x = parent[x]
            return x

        def union(a: int, b: int) -> bool:
            root_a = find(a)
            root_b = find(b)
            if root_a == root_b:
                return False
            if rank[root_a] < rank[root_b]:
                root_a, root_b = root_b, root_a
            parent[root_b] = root_a
            if rank[root_a] == rank[root_b]:
                rank[root_a] += 1
            return True

        total = 0
        used = 0
        for a, b, cost in sorted(connections, key=lambda item: item[2]):
            if union(a, b):
                total += cost
                used += 1
                if used == n - 1:
                    return total

        return -1
