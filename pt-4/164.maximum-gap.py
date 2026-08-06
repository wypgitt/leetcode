"""
Approach: Bucket sort using the pigeonhole principle.
Data structure: buckets store only minimum and maximum values for each value range; internal bucket gaps cannot beat the chosen bucket size.
Interview logic: for n numbers between lo and hi, the maximum adjacent sorted gap is at least ceil((hi-lo)/(n-1)). Put numbers in buckets of that size and only compare consecutive non-empty bucket boundaries.
Complexity: O(n) time, O(n) space.
Tests and edge cases: fewer than two numbers returns 0; all equal numbers return 0; very sparse values produce empty buckets that create large gaps.
"""
from __future__ import annotations
from typing import List

# @lc code=start
class Solution:
    def maximumGap(self, nums: List[int]) -> int:
        n = len(nums)
        if n < 2:
            return 0
        lo, hi = min(nums), max(nums)
        if lo == hi:
            return 0
        size = max(1, (hi - lo + n - 2) // (n - 1))
        count = (hi - lo) // size + 1
        buckets = [[None, None] for _ in range(count)]
        for num in nums:
            b = (num - lo) // size
            buckets[b][0] = num if buckets[b][0] is None else min(buckets[b][0], num)
            buckets[b][1] = num if buckets[b][1] is None else max(buckets[b][1], num)
        best = 0
        prev_max = None
        for bmin, bmax in buckets:
            if bmin is None:
                continue
            if prev_max is not None:
                best = max(best, bmin - prev_max)
            prev_max = bmax
        return best
# @lc code=end
