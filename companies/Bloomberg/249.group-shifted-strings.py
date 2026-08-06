"""
Approach: Group strings by their circular shift pattern.
Data structure: a dictionary maps a tuple of normalized character offsets to all strings with that pattern.
Interview logic: shifting every character by the same amount makes the first character effectively zero; the remaining offsets modulo 26 identify the whole shift class.
Complexity: O(total characters) time and space.
Tests and edge cases: single-character strings all share the empty pattern; wraparound like az and ba match; groups may be returned in any order.
"""
from __future__ import annotations
from collections import defaultdict
from typing import List

# @lc code=start
from collections import defaultdict
class Solution:
    def groupStrings(self, strings: List[str]) -> List[List[str]]:
        groups = defaultdict(list)
        for s in strings:
            base = ord(s[0])
            key = tuple((ord(ch) - base) % 26 for ch in s)
            groups[key].append(s)
        return list(groups.values())
# @lc code=end
