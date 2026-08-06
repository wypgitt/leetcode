"""
Approach: Compare strings at the first mismatch and check the only possible edit.
Data structure: indexes only; no DP table is needed because exactly one edit is allowed.
Interview logic: if lengths differ by more than one, impossible. At the first mismatch, equal lengths require replacing one char; unequal lengths require deleting one char from the longer string. If no mismatch occurs, strings are one edit apart only when their lengths differ by one.
Complexity: O(n) time, O(1) space.
Tests and edge cases: identical strings return False; empty vs one char returns True; empty vs empty returns False.
"""
from __future__ import annotations

# @lc code=start
class Solution:
    def isOneEditDistance(self, s: str, t: str) -> bool:
        if abs(len(s) - len(t)) > 1:
            return False
        if len(s) > len(t):
            s, t = t, s
        for i in range(len(s)):
            if s[i] != t[i]:
                if len(s) == len(t):
                    return s[i + 1:] == t[i + 1:]
                return s[i:] == t[i + 1:]
        return len(t) - len(s) == 1
# @lc code=end
