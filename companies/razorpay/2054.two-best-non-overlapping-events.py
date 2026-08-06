#
# @lc app=leetcode id=2054 lang=python3
#
# [2054] Two Best Non-Overlapping Events
#
# https://leetcode.com/problems/two-best-non-overlapping-events/description/
#
# algorithms
# Medium (63.96%)
# Likes:    1871
# Dislikes: 73
# Total Accepted:    181.3K
# Total Submissions: 283.5K
# Testcase Example:  "[[1,3,2],[4,5,2],[2,4,3]]"
#
# You are given a 0-indexed 2D integer array of events where events[i] =
# [startTime_i, endTime_i, value_i]. The i^th event starts at startTime_i_ and
# ends at endTime_i, and if you attend this event, you will receive a value of
# value_i. You can choose at most two non-overlapping events to attend such that
# the sum of their values is maximized.
#
# Return this maximum sum.
#
# Note that the start time and end time is inclusive: that is, you cannot attend
# two events where one of them starts and the other ends at the same time. More
# specifically, if you attend an event with end time t, the next event must
# start at or after t + 1.
#
#
#
# Example 1:
#
# Input: events = [[1,3,2],[4,5,2],[2,4,3]]
# Output: 4
# Explanation: Choose the green events, 0 and 1 for a sum of 2 + 2 = 4.
#
# Example 2:
#
# Input: events = [[1,3,2],[4,5,2],[1,5,5]]
# Output: 5
# Explanation: Choose event 2 for a sum of 5.
#
# Example 3:
#
# Input: events = [[1,5,3],[1,5,1],[6,6,5]]
# Output: 8
# Explanation: Choose events 0 and 2 for a sum of 3 + 5 = 8.
#
#
#
# Constraints:
#
#
# 2 <= events.length <= 10^5
#
#
# events[i].length == 3
#
#
# 1 <= startTime_i <= endTime_i <= 10^9
#
#
# 1 <= value_i <= 10^6
#

# @lc code=start
from typing import List
import bisect
import heapq


class Solution:
    def maxTwoEvents(self, events: List[List[int]]) -> int:
        """
        Interview explanation:
        Choose at most two non-overlapping events (end_i < start_j) maximizing
        total value (single event allowed).

        Algorithm:
        - Sort by end time; for each event binary-search last end < start;
          combine with prefix-max value among those ended events.

        Complexity: O(n log n) time, O(n) space.
        """
        events.sort(key=lambda e: e[1])
        ends = [e[1] for e in events]
        pref = [0] * len(events)
        ans = 0
        for i, (s, e, v) in enumerate(events):
            pref[i] = max(pref[i - 1] if i else 0, v)
            ans = max(ans, v)
            j = bisect.bisect_left(ends, s) - 1
            if j >= 0:
                ans = max(ans, v + pref[j])
        return ans

    def maxTwoEvents_heap(self, events: List[List[int]]) -> int:
        """
        Interview explanation:
        Alternate classic: sort by start; maintain heap of (end, value) and
        running max among finished events.

        Algorithm:
        - Process events by start; pop finished from heap into max_finished;
          ans = max(v, v+max_finished).

        Complexity: O(n log n) time, O(n) space.
        """
        events.sort()
        pq = []
        max_finished = 0
        ans = 0
        for s, e, v in events:
            while pq and pq[0][0] < s:
                max_finished = max(max_finished, heapq.heappop(pq)[1])
            ans = max(ans, v, max_finished + v)
            heapq.heappush(pq, (e, v))
        return ans
# @lc code=end
