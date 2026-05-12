#
# @lc app=leetcode id=1353 lang=python3
#
# [1353] Maximum Number of Events That Can Be Attended
#
# https://leetcode.com/problems/maximum-number-of-events-that-can-be-attended/description/
#
# algorithms
# Medium (38.96%)
# Likes:    4012
# Dislikes: 636
# Total Accepted:    228K
# Total Submissions: 585.1K
# Testcase Example:  '[[1,2],[2,3],[3,4]]'
#
# You are given an array of events where events[i] = [startDayi, endDayi].
# Every event i starts at startDayi and ends at endDayi.
# 
# You can attend an event i at any day d where startDayi <= d <= endDayi. You
# can only attend one event at any time d.
# 
# Return the maximum number of events you can attend.
# 
# 
# Example 1:
# 
# 
# Input: events = [[1,2],[2,3],[3,4]]
# Output: 3
# Explanation: You can attend all the three events.
# One way to attend them all is as shown.
# Attend the first event on day 1.
# Attend the second event on day 2.
# Attend the third event on day 3.
# 
# 
# Example 2:
# 
# 
# Input: events= [[1,2],[2,3],[3,4],[1,2]]
# Output: 4
# 
# 
# 
# Constraints:
# 
# 
# 1 <= events.length <= 10^5
# events[i].length == 2
# 1 <= startDayi <= endDayi <= 10^5
# 
# 
#

# @lc code=start
from __future__ import annotations

from heapq import heappop, heappush
from typing import List


class Solution:
    def maxEvents(self, events: List[List[int]]) -> int:
        events.sort()
        min_heap = []
        day = 0
        index = 0
        attended = 0

        while index < len(events) or min_heap:
            if not min_heap:
                day = max(day, events[index][0])

            while index < len(events) and events[index][0] <= day:
                heappush(min_heap, events[index][1])
                index += 1

            while min_heap and min_heap[0] < day:
                heappop(min_heap)

            if min_heap:
                heappop(min_heap)
                attended += 1
                day += 1

        return attended
# @lc code=end

#
# Interview explanation
# ---------------------
# Idea:
# On each day, attend the available event that ends earliest. This greedy
# choice leaves longer-lasting events available for future days and prevents
# urgent events from expiring.
#
# Data structure:
# Sort events by start day, then use a min-heap of end days for events that
# have started but not yet been attended or expired.
#
# Walkthrough:
# 1. Sort events by start day.
# 2. If no event is available, jump `day` forward to the next event start.
# 3. Add all events whose start day is <= current day to the heap.
# 4. Remove expired events with end day < current day.
# 5. Attend the event with smallest end day, increment answer, and move to the
#    next day.
#
# Edge cases:
# - Gaps between event days: jumping avoids scanning empty days.
# - Same start/end days: heap tie order is irrelevant because one event per day.
# - Expired events: removed before attendance.
#
# Complexity:
# - Time: O(n log n), sorting plus heap operations.
# - Space: O(n) for the heap.
