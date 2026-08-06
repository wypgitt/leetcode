"""
Approach: Greedy candidate reset after any negative tank prefix.
Data structure: scalar totals and current tank balance are sufficient.
Interview logic: if total gas is less than total cost, no start can work. Otherwise, when the tank from a candidate start becomes negative at i, every station from that candidate through i is impossible, so the next candidate is i + 1.
Complexity: O(n) time, O(1) space.
Tests and edge cases: impossible total returns -1; single station works iff gas >= cost; the final candidate may conceptually wrap around.
"""
from __future__ import annotations
from typing import List

# @lc code=start
class Solution:
    def canCompleteCircuit(self, gas: List[int], cost: List[int]) -> int:
        if sum(gas) < sum(cost):
            return -1
        start = tank = 0
        for i, (g, c) in enumerate(zip(gas, cost)):
            tank += g - c
            if tank < 0:
                start = i + 1
                tank = 0
        return start
# @lc code=end
