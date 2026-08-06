"""
Approach: Add both rectangle areas and subtract their overlap area.
Data structure: scalar coordinate calculations are sufficient.
Interview logic: overlap width is max(0, min(right edges) - max(left edges)); overlap height is computed the same way for y. If either is zero, there is no overlap.
Complexity: O(1) time and space.
Tests and edge cases: no overlap; touching edges produce zero overlap; one rectangle partially or fully covers another.
"""
from __future__ import annotations

# @lc code=start
class Solution:
    def computeArea(self, ax1: int, ay1: int, ax2: int, ay2: int, bx1: int, by1: int, bx2: int, by2: int) -> int:
        area_a = (ax2 - ax1) * (ay2 - ay1)
        area_b = (bx2 - bx1) * (by2 - by1)
        overlap_w = max(0, min(ax2, bx2) - max(ax1, bx1))
        overlap_h = max(0, min(ay2, by2) - max(ay1, by1))
        return area_a + area_b - overlap_w * overlap_h
# @lc code=end
