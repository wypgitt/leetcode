"""
Approach: Compare integer revision parts from left to right.
Data structure: arrays of split components are sufficient; converting to int removes leading-zero differences.
Interview logic: missing revision fields are treated as zero, so pad conceptually while comparing. The first unequal component decides the answer.
Complexity: O(n + m) time and space for the split version strings.
Tests and edge cases: leading zeros; different number of components; equal versions like 1.0 and 1.0.0.
"""
from __future__ import annotations

# @lc code=start
class Solution:
    def compareVersion(self, version1: str, version2: str) -> int:
        a = [int(x) for x in version1.split('.')]
        b = [int(x) for x in version2.split('.')]
        for i in range(max(len(a), len(b))):
            x = a[i] if i < len(a) else 0
            y = b[i] if i < len(b) else 0
            if x < y:
                return -1
            if x > y:
                return 1
        return 0
# @lc code=end
