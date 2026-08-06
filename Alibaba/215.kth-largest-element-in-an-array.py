"""
Approach: Maintain a min-heap of the k largest values seen so far.
Data structure: the heap root is the smallest among the current top k, so it is the kth largest after all numbers are processed.
Interview logic: push each number and, when the heap grows past k, remove the smallest. Everything removed cannot be in the top k because there are already k larger-or-equal values kept.
Complexity: O(n log k) time, O(k) space. Quickselect can improve average time to O(n) but has more implementation edge cases.
Tests and edge cases: duplicates count as separate elements; k=1 returns max; k=len(nums) returns min.
"""
from __future__ import annotations
import heapq
from typing import List

# @lc code=start
import heapq
class Solution:
    def findKthLargest(self, nums: List[int], k: int) -> int:
        heap: List[int] = []
        for num in nums:
            heapq.heappush(heap, num)
            if len(heap) > k:
                heapq.heappop(heap)
        return heap[0]
# @lc code=end
