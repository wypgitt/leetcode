from __future__ import annotations

from typing import List


class Solution:
    def maxDepthAfterSplit(self, seq: str) -> List[int]:
        answer = []
        depth = 0

        for char in seq:
            if char == "(":
                depth += 1
                answer.append(depth & 1)
            else:
                answer.append(depth & 1)
                depth -= 1

        return answer

