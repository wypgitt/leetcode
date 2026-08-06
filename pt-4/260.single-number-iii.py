"""
Approach: XOR all values, then partition by one differing bit.
Data structure: integer bit masks keep constant space.
Interview logic: duplicates cancel in the total XOR, leaving a ^ b for the two unique numbers. Any set bit in a ^ b differs between a and b; partitioning numbers by that bit puts a and b in separate groups, where duplicates still cancel.
Complexity: O(n) time, O(1) space.
Tests and edge cases: two-element input returns both; negative numbers work with XOR; answer order is arbitrary.
"""
from __future__ import annotations
from typing import List

# @lc code=start
class Solution:
    def singleNumber(self, nums: List[int]) -> List[int]:
        xor_all = 0
        for num in nums:
            xor_all ^= num
        mask = xor_all & -xor_all
        a = 0
        for num in nums:
            if num & mask:
                a ^= num
        return [a, xor_all ^ a]
# @lc code=end
