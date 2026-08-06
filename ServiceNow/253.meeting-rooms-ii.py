"""
Approach: Sweep meetings by start time with a min-heap of end times.
Data structure: the heap stores the end time of every room currently in use; the smallest end time is the room that frees first.
Interview logic: before starting a meeting, pop all rooms that have ended. Then allocate the current meeting's room by pushing its end. The maximum heap size is the room count needed.
Complexity: O(n log n) time, O(n) space.
Tests and edge cases: empty intervals return 0; touching intervals like [1,2] and [2,3] reuse a room; fully overlapping intervals require n rooms.
"""
from __future__ import annotations
import heapq
from typing import List

# @lc code=start
import heapq
class Solution:
    def minMeetingRooms(self, intervals: List[List[int]]) -> int:
        if not intervals:
            return 0
        intervals.sort(key=lambda x: x[0])
        heap = []
        best = 0
        for start, end in intervals:
            while heap and heap[0] <= start:
                heapq.heappop(heap)
            heapq.heappush(heap, end)
            best = max(best, len(heap))
        return best
# @lc code=end
