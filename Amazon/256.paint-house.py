"""
Approach: Dynamic programming over houses and previous colors.
Data structure: three scalar costs store the minimum total ending with red, blue, or green for the previous house.
Interview logic: to paint the current house a color, add that color's cost to the minimum previous total among the other two colors.
Complexity: O(n) time, O(1) space.
Tests and edge cases: empty costs returns 0; one house returns min of its costs; adjacent houses cannot use the same color.
"""
from __future__ import annotations
from typing import List

# @lc code=start
class Solution:
    def minCost(self, costs: List[List[int]]) -> int:
        if not costs:
            return 0
        red = blue = green = 0
        for r, b, g in costs:
            red, blue, green = r + min(blue, green), b + min(red, green), g + min(red, blue)
        return min(red, blue, green)
# @lc code=end
