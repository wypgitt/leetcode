from __future__ import annotations

from collections import defaultdict
from typing import DefaultDict, List


class Solution:
    def smallestStringWithSwaps(self, s: str, pairs: List[List[int]]) -> str:
        parent = list(range(len(s)))
        rank = [0] * len(s)

        def find(x: int) -> int:
            while parent[x] != x:
                parent[x] = parent[parent[x]]
                x = parent[x]
            return x

        def union(a: int, b: int) -> None:
            root_a = find(a)
            root_b = find(b)
            if root_a == root_b:
                return
            if rank[root_a] < rank[root_b]:
                root_a, root_b = root_b, root_a
            parent[root_b] = root_a
            if rank[root_a] == rank[root_b]:
                rank[root_a] += 1

        for a, b in pairs:
            union(a, b)

        characters: DefaultDict[int, List[str]] = defaultdict(list)
        for index, char in enumerate(s):
            characters[find(index)].append(char)

        for group in characters.values():
            group.sort(reverse=True)

        result = []
        for index in range(len(s)):
            result.append(characters[find(index)].pop())

        return "".join(result)

