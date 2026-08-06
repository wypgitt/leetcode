#
# @lc app=leetcode id=252 lang=python3
#
# [252] Meeting Rooms
#
# https://leetcode.com/problems/meeting-rooms/description/
#
# algorithms
# Easy (59.52%)
# Likes:    2131
# Dislikes: 117
# Total Accepted:    529.2K
# Total Submissions: 889.2K
# Testcase Example:  "[[0,30],[5,10],[15,20]]"
#
#
# You are given an array of meeting times intervals where intervals[i] =
# [start_i, end_i].
#
# A person can attend all meetings if no two meeting intervals overlap.
# Meetings ending at time t and starting at time t do not overlap.
#
# ​​​​​​​Return true if a person can attend all meetings. Otherwise,
# return false.
#
# Example 1:
#
# Input: intervals = [[0,30],[5,10],[15,20]]
# Output: false
#
# Example 2:
#
# Input: intervals = [[7,10],[2,4]]
# Output: true
#
# Constraints:
#
# 0 <= intervals.length <= 10^4
#
# intervals[i].length == 2
#
# 0 <= start_i < end_i <= 10^6
#
# @lc code=start
from typing import List


class Solution:
    def canAttendMeetings(self, intervals: List[List[int]]) -> bool:
        """
        Interview explanation:
        Sort by start time; a person can attend all meetings iff no two
        consecutive intervals overlap (prev end > next start).

        Algorithm:
        - Sort intervals by start.
        - For each adjacent pair, if intervals[i-1][1] > intervals[i][0], False.
        - Else True.

        Complexity: O(n log n) time, O(1) or O(n) space depending on sort.
        """
        intervals.sort(key=lambda x: x[0])
        for i in range(1, len(intervals)):
            if intervals[i][0] < intervals[i - 1][1]:
                return False
        return True
# @lc code=end
