#
# @lc app=leetcode id=1353 lang=python3
#
# [1353] Maximum Number of Events That Can Be Attended
#
# https://leetcode.com/problems/maximum-number-of-events-that-can-be-attended/description/
#
# algorithms
# Medium (39.04%)
# Likes:    4048
# Dislikes: 638
# Total Accepted:    233K
# Total Submissions: 598K
# Testcase Example:  "[[1,2],[2,3],[3,4]]"
#
# You are given an array of events where events[i] = [startDay_i, endDay_i].
# Every event i starts at startDay_i_ and ends at endDay_i.
#
# You can attend an event i at any day d where startDay_i <= d <= endDay_i. You
# can only attend one event at any time d.
#
# Return the maximum number of events you can attend.
#
# Example 1:
#
# Input: events = [[1,2],[2,3],[3,4]]
# Output: 3
# Explanation: You can attend all the three events.
# One way to attend them all is as shown.
# Attend the first event on day 1.
# Attend the second event on day 2.
# Attend the third event on day 3.
#
# Example 2:
#
# Input: events= [[1,2],[2,3],[3,4],[1,2]]
# Output: 4
#
# Constraints:
#
# 1 <= events.length <= 10^5
#
# events[i].length == 2
#
# 1 <= startDay_i <= endDay_i <= 10^5
#

# @lc code=start

import heapq
from typing import List


class Solution:
    def maxEvents(self, events: List[List[int]]) -> int:
        """
        Interview explanation:
        Attend at most one event per day. Greedy: each day attend the available
        event that ends soonest. Process days with a min-heap of end times.

        Algorithm:
        - Sort by start; day from min start to max end
        - Push ending days of events starting today; pop expired; attend earliest end

        Complexity: O(D + n log n) with D span of days (or compress via jumps).
        """
        events.sort()
        i, n = 0, len(events)
        day = 0
        ans = 0
        hq: List[int] = []
        max_day = max(e[1] for e in events)
        day = events[0][0]
        while day <= max_day:
            while i < n and events[i][0] == day:
                heapq.heappush(hq, events[i][1])
                i += 1
            while hq and hq[0] < day:
                heapq.heappop(hq)
            if hq:
                heapq.heappop(hq)
                ans += 1
            if not hq and i < n:
                day = events[i][0]
            else:
                day += 1
        return ans
# @lc code=end
