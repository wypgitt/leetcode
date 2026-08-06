#
# @lc app=leetcode id=3440 lang=python3
#
# [3440] Reschedule Meetings for Maximum Free Time II
#
# https://leetcode.com/problems/reschedule-meetings-for-maximum-free-time-ii/description/
#
# algorithms
# Medium (60.36%)
# Likes:    471
# Dislikes: 26
# Total Accepted:    85.1K
# Total Submissions: 140.9K
# Testcase Example:  "5\n[1,3]\n[2,5]"
#
#
# You are given an integer eventTime denoting the duration of an event.
# You are also given two integer arrays startTime and endTime, each of
# length n.
#
# These represent the start and end times of n non-overlapping meetings
# that occur during the event between time t = 0 and time t = eventTime,
# where the i^th meeting occurs during the time [startTime[i],
# endTime[i]].
#
# You can reschedule at most one meeting by moving its start time while
# maintaining the same duration, such that the meetings remain
# non-overlapping, to maximize the longest continuous period of free time
# during the event.
#
# Return the maximum amount of free time possible after rearranging the
# meetings.
#
# Note that the meetings can not be rescheduled to a time outside the
# event and they should remain non-overlapping.
#
# Note: In this version, it is valid for the relative ordering of the
# meetings to change after rescheduling one meeting.
#
# Example 1:
#
# Input: eventTime = 5, startTime = [1,3], endTime = [2,5]
#
# Output: 2
#
# Explanation:
#
# Reschedule the meeting at [1, 2] to [2, 3], leaving no meetings during
# the time [0, 2].
#
# Example 2:
#
# Input: eventTime = 10, startTime = [0,7,9], endTime = [1,8,10]
#
# Output: 7
#
# Explanation:
#
# Reschedule the meeting at [0, 1] to [8, 9], leaving no meetings during
# the time [0, 7].
#
# Example 3:
#
# Input: eventTime = 10, startTime = [0,3,7,9], endTime = [1,4,8,10]
#
# Output: 6
#
# Explanation:
#
# Reschedule the meeting at [3, 4] to [8, 9], leaving no meetings during
# the time [1, 7].
#
# Example 4:
#
# Input: eventTime = 5, startTime = [0,1,2,3,4], endTime = [1,2,3,4,5]
#
# Output: 0
#
# Explanation:
#
# There is no time during the event not occupied by meetings.
#
# Constraints:
#
# 1 <= eventTime <= 10^9
#
# n == startTime.length == endTime.length
#
# 2 <= n <= 10^5
#
# 0 <= startTime[i] < endTime[i] <= eventTime
#
# endTime[i] <= startTime[i + 1] where i lies in the range [0, n - 2].
#

# @lc code=start
from typing import List


class Solution:
    def maxFreeTime(
        self, eventTime: int, startTime: List[int], endTime: List[int]
    ) -> int:
        """
        Interview explanation:
        Reschedule at most one meeting (order may change). For meeting i, merging
        its two adjacent gaps always yields gaps[i]+gaps[i+1]; if its duration
        fits in some other gap, we can move it away and also reclaim the duration.

        Algorithm:
        - Build gaps; prefix/suffix max gaps.
        - For each i: ans = max(ans, gaps[i]+gaps[i+1] + duration if duration
          fits in max gap outside {i,i+1}, else just the adjacent sum).

        Complexity: O(n) time, O(n) space.
        """
        n = len(startTime)
        gaps = (
            [startTime[0]]
            + [startTime[i] - endTime[i - 1] for i in range(1, n)]
            + [eventTime - endTime[-1]]
        )
        max_left = [0] * (n + 1)
        max_right = [0] * (n + 1)
        max_left[0] = gaps[0]
        max_right[n] = gaps[n]
        for i in range(1, n + 1):
            max_left[i] = max(gaps[i], max_left[i - 1])
        for i in range(n - 1, -1, -1):
            max_right[i] = max(gaps[i], max_right[i + 1])

        ans = 0
        for i in range(n):
            dur = endTime[i] - startTime[i]
            adjacent = gaps[i] + gaps[i + 1]
            can_move = dur <= max(
                max_left[i - 1] if i > 0 else 0,
                max_right[i + 2] if i + 2 < n + 1 else 0,
            )
            ans = max(ans, adjacent + (dur if can_move else 0))
        return ans
# @lc code=end
