#
# @lc app=leetcode id=2446 lang=python3
#
# [2446] Determine if Two Events Have Conflict
#
# https://leetcode.com/problems/determine-if-two-events-have-conflict/description/
#
# algorithms
# Easy (53.49%)
# Likes:    544
# Dislikes: 73
# Total Accepted:    67.6K
# Total Submissions: 126.4K
# Testcase Example:  "[\"01:15\",\"02:00\"]\n[\"02:00\",\"03:00\"]"
#
# You are given two arrays of strings that represent two inclusive events that
# happened on the same day, event1 and event2, where:
#
#
# event1 = [startTime_1, endTime_1] and
#
#
# event2 = [startTime_2, endTime_2].
#
# Event times are valid 24 hours format in the form of HH:MM.
#
# A conflict happens when two events have some non-empty intersection (i.e.,
# some moment is common to both events).
#
# Return true if there is a conflict between two events. Otherwise, return
# false.
#
#
#
# Example 1:
#
# Input: event1 = ["01:15","02:00"], event2 = ["02:00","03:00"]
# Output: true
# Explanation: The two events intersect at time 2:00.
#
# Example 2:
#
# Input: event1 = ["01:00","02:00"], event2 = ["01:20","03:00"]
# Output: true
# Explanation: The two events intersect starting from 01:20 to 02:00.
#
# Example 3:
#
# Input: event1 = ["10:00","11:00"], event2 = ["14:00","15:00"]
# Output: false
# Explanation: The two events do not intersect.
#
#
#
# Constraints:
#
#
# event1.length == event2.length == 2
#
#
# event1[i].length == event2[i].length == 5
#
#
# startTime_1 <= endTime_1
#
#
# startTime_2 <= endTime_2
#
#
# All the event times follow the HH:MM format.
#

# @lc code=start
from typing import List


class Solution:
    def haveConflict(self, event1: List[str], event2: List[str]) -> bool:
        """
        Interview explanation:
        Inclusive [start,end] events as HH:MM; return whether they overlap.

        Algorithm:
        - start1 <= end2 and start2 <= end1 (lexicographic works for HH:MM).

        Complexity: O(1).
        """
        return event1[0] <= event2[1] and event2[0] <= event1[1]
# @lc code=end
