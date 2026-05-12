from __future__ import annotations

from bisect import bisect_right
from typing import List


class Solution:
    def numSmallerByFrequency(self, queries: List[str], words: List[str]) -> List[int]:
        def frequency(word: str) -> int:
            smallest = min(word)
            return word.count(smallest)

        word_frequencies = sorted(frequency(word) for word in words)
        return [
            len(word_frequencies) - bisect_right(word_frequencies, frequency(query))
            for query in queries
        ]

