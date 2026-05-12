from __future__ import annotations

from collections import Counter
from typing import List


class Solution:
    def smallestCommonElement(self, mat: List[List[int]]) -> int:
        count = Counter()
        for row in mat:
            count.update(row)

        for value in mat[0]:
            if count[value] == len(mat):
                return value

        return -1

