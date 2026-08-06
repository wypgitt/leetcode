"""
Approach: Recursively build numbers from the center outward using valid rotated digit pairs.
Data structure: recursion returns all valid inner strings for a target remaining length.
Interview logic: each outer pair must be one of 00, 11, 69, 88, 96, but the outermost layer cannot be 00 for n > 1. Odd centers can be 0, 1, or 8.
Complexity: O(5^(n/2) * n) time and output space.
Tests and edge cases: n=1 includes 0; n=2 excludes 00; even and odd lengths use different bases.
"""
from __future__ import annotations
from typing import List

# @lc code=start
class Solution:
    def findStrobogrammatic(self, n: int) -> List[str]:
        pairs = [('0', '0'), ('1', '1'), ('6', '9'), ('8', '8'), ('9', '6')]
        def build(length: int, total: int) -> List[str]:
            if length == 0:
                return ['']
            if length == 1:
                return ['0', '1', '8']
            ans = []
            for inner in build(length - 2, total):
                for a, b in pairs:
                    if length == total and a == '0':
                        continue
                    ans.append(a + inner + b)
            return ans
        return build(n, n)
# @lc code=end
