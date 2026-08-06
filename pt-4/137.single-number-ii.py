"""
Approach: Bit-count state machine using two integer masks.
Data structure: ones and twos encode each bit's count modulo 3 across all bit positions in parallel.
Interview logic: each incoming number moves bits through states 00 -> 01 -> 10 -> 00. Bits appearing three times clear out, leaving the unique number in ones.
Complexity: O(n) time, O(1) space.
Tests and edge cases: zero works; negative integers work with the same bit identities in Python; triples cancel regardless of order.
"""
from __future__ import annotations
from typing import List

# @lc code=start
class Solution:
    def singleNumber(self, nums: List[int]) -> int:
        ones = twos = 0
        for num in nums:
            ones = (ones ^ num) & ~twos
            twos = (twos ^ num) & ~ones
        return ones
# @lc code=end
