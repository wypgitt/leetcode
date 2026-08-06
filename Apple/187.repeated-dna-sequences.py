"""
Approach: Track seen 10-character windows and collect windows seen twice.
Data structure: two sets distinguish first sightings from already-reported repeated sequences.
Interview logic: every valid DNA substring has fixed length 10, so scanning all windows is enough. The output set prevents duplicates in the answer.
Complexity: O(n) time and O(n) space, with constant-size substring copies.
Tests and edge cases: strings shorter than 10 return []; overlapping repeats are allowed; a sequence repeated many times appears once.
"""
from __future__ import annotations
from typing import List

# @lc code=start
class Solution:
    def findRepeatedDnaSequences(self, s: str) -> List[str]:
        seen, repeated = set(), set()
        for i in range(len(s) - 9):
            window = s[i:i + 10]
            if window in seen:
                repeated.add(window)
            else:
                seen.add(window)
        return list(repeated)
# @lc code=end
