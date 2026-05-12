from __future__ import annotations

from typing import List


class Solution:
    def minSwaps(self, data: List[int]) -> int:
        ones = sum(data)
        if ones <= 1:
            return 0

        zeros = ones - sum(data[:ones])
        best = zeros
        for right in range(ones, len(data)):
            if data[right] == 0:
                zeros += 1
            if data[right - ones] == 0:
                zeros -= 1
            best = min(best, zeros)

        return best

