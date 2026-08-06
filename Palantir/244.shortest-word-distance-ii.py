"""
Approach: Preprocess positions for every word, then answer queries with two pointers.
Data structure: a dictionary maps each word to its sorted list of indices in wordsDict.
Interview logic: for two sorted position lists, the closest pair can be found by advancing the pointer at the smaller index, because that is the only move that can reduce the current distance.
Complexity: O(n) preprocessing; O(a + b) per query for occurrence counts a and b; O(n) space.
Tests and edge cases: repeated queries benefit from preprocessing; words can appear many times; the two queried words are distinct by this problem's contract.
"""
from __future__ import annotations
from collections import defaultdict
from typing import List

# @lc code=start
from collections import defaultdict
class WordDistance:
    def __init__(self, wordsDict: List[str]):
        self.positions = defaultdict(list)
        for i, word in enumerate(wordsDict):
            self.positions[word].append(i)

    def shortest(self, word1: str, word2: str) -> int:
        a, b = self.positions[word1], self.positions[word2]
        i = j = 0
        best = float('inf')
        while i < len(a) and j < len(b):
            best = min(best, abs(a[i] - b[j]))
            if a[i] < b[j]:
                i += 1
            else:
                j += 1
        return best
# @lc code=end
