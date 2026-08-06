"""
Approach: Single scan tracking recent relevant positions.
Data structure: integer indexes track the latest occurrence of each target word.
Interview logic: if the words differ, update the matching latest index and compare when both exist. If the words are the same, the shortest distance is between consecutive occurrences of that word.
Complexity: O(n) time, O(1) space.
Tests and edge cases: word1 == word2; adjacent occurrences produce distance 1; non-adjacent repeated targets update the best distance.
"""
from __future__ import annotations
from typing import List

# @lc code=start
class Solution:
    def shortestWordDistance(self, wordsDict: List[str], word1: str, word2: str) -> int:
        best = float('inf')
        if word1 == word2:
            prev = -1
            for i, word in enumerate(wordsDict):
                if word == word1:
                    if prev != -1:
                        best = min(best, i - prev)
                    prev = i
            return best
        last1 = last2 = -1
        for i, word in enumerate(wordsDict):
            if word == word1:
                last1 = i
                if last2 != -1:
                    best = min(best, abs(last1 - last2))
            elif word == word2:
                last2 = i
                if last1 != -1:
                    best = min(best, abs(last1 - last2))
        return best
# @lc code=end
