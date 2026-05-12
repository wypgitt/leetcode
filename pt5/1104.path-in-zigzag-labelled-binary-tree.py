from __future__ import annotations

from typing import List


class Solution:
    def pathInZigZagTree(self, label: int) -> List[int]:
        path = []

        while label:
            path.append(label)
            level_start = 1 << (label.bit_length() - 1)
            level_end = (level_start << 1) - 1
            label = (level_start + level_end - label) // 2

        return path[::-1]

