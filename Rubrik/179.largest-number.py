"""
Approach: Sort numbers by concatenation order.
Data structure: a custom comparator decides whether x should come before y by comparing x+y and y+x.
Interview logic: the globally largest concatenation is achieved by putting any pair in the order that forms the larger two-number string. Sorting with that pairwise rule gives the optimal arrangement.
Complexity: O(n log n * k) time where k is max digit length, O(nk) space for strings.
Tests and edge cases: all zeros should return '0'; prefixes like 3 and 30 require comparator logic; single number returns itself.
"""
from __future__ import annotations
from functools import cmp_to_key
from typing import List

# @lc code=start
from functools import cmp_to_key
class Solution:
    def largestNumber(self, nums: List[int]) -> str:
        parts = [str(num) for num in nums]
        def cmp(a: str, b: str) -> int:
            if a + b > b + a:
                return -1
            if a + b < b + a:
                return 1
            return 0
        ans = ''.join(sorted(parts, key=cmp_to_key(cmp)))
        return '0' if ans[0] == '0' else ans
# @lc code=end
