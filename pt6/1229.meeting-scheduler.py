#
# @lc app=leetcode id=1229 lang=python3
#
# [1229] Meeting Scheduler
#
# https://leetcode.com/problems/meeting-scheduler/description/
#
# algorithms
# Medium (55.20%)
# Likes:    957
# Dislikes: 39
# Total Accepted:    105.6K
# Total Submissions: 191.2K
# Testcase Example:  '[[10,50],[60,120],[140,210]]\n[[0,15],[60,70]]\n8'
#
# Given the availability time slots arrays slots1 and slots2 of two people and
# a meeting duration duration, return the earliest time slot that works for
# both of them and is of duration duration.
# 
# If there is no common time slot that satisfies the requirements, return an
# empty array.
# 
# The format of a time slot is an array of two elements [start, end]
# representing an inclusive time range from start to end.
# 
# It is guaranteed that no two availability slots of the same person intersect
# with each other. That is, for any two time slots [start1, end1] and [start2,
# end2] of the same person, either start1 > end2 or start2 > end1.
# 
# 
# Example 1:
# 
# 
# Input: slots1 = [[10,50],[60,120],[140,210]], slots2 = [[0,15],[60,70]],
# duration = 8
# Output: [60,68]
# 
# 
# Example 2:
# 
# 
# Input: slots1 = [[10,50],[60,120],[140,210]], slots2 = [[0,15],[60,70]],
# duration = 12
# Output: []
# 
# 
# 
# Constraints:
# 
# 
# 1 <= slots1.length, slots2.length <= 10^4
# slots1[i].length, slots2[i].length == 2
# slots1[i][0] < slots1[i][1]
# slots2[i][0] < slots2[i][1]
# 0 <= slots1[i][j], slots2[i][j] <= 10^9
# 1 <= duration <= 10^6
# 
# 
#

# @lc code=start
from typing import List


class Solution:
    def minAvailableDuration(self, slots1: List[List[int]], slots2: List[List[int]], duration: int) -> List[int]:
        slots1.sort()
        slots2.sort()
        i = j = 0

        while i < len(slots1) and j < len(slots2):
            start = max(slots1[i][0], slots2[j][0])
            end = min(slots1[i][1], slots2[j][1])

            if end - start >= duration:
                return [start, start + duration]

            if slots1[i][1] < slots2[j][1]:
                i += 1
            else:
                j += 1

        return []
# @lc code=end

# Explanation
# -----------
# Sort both availability lists, then use two pointers to compare the current
# slots. Their overlap is [max(starts), min(ends)]. If that overlap is at
# least duration, it is the earliest possible meeting because both lists are
# processed in chronological order.
#
# If the overlap is too short, advance the slot that ends earlier. That slot
# cannot overlap any future slot from the other list better, because future
# slots start no earlier than the current one.
#
# Edge cases: no overlap returns []; exact-length overlap is valid; unsorted
# input is normalized by sorting.
#
# Time complexity: O(n log n + m log m) for sorting plus O(n + m) scanning.
# Space complexity: O(1) beyond sorting overhead.
