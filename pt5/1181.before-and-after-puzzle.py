from __future__ import annotations

from typing import List


class Solution:
    def beforeAndAfterPuzzles(self, phrases: List[str]) -> List[str]:
        words = [phrase.split() for phrase in phrases]
        puzzles = set()

        for i, first_words in enumerate(words):
            for j, second_words in enumerate(words):
                if i == j:
                    continue
                if first_words[-1] == second_words[0]:
                    tail = " ".join(second_words[1:])
                    puzzles.add(phrases[i] if not tail else phrases[i] + " " + tail)

        return sorted(puzzles)

