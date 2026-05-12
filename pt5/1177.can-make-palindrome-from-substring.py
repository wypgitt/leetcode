from __future__ import annotations

from typing import List


class Solution:
    def canMakePaliQueries(self, s: str, queries: List[List[int]]) -> List[bool]:
        prefix = [0]
        mask = 0

        for char in s:
            mask ^= 1 << (ord(char) - ord("a"))
            prefix.append(mask)

        answer = []
        for left, right, k in queries:
            odd_mask = prefix[right + 1] ^ prefix[left]
            odd_count = odd_mask.bit_count()
            answer.append(odd_count // 2 <= k)

        return answer

