#
# @lc app=leetcode id=759 lang=python3
#
# [759] Employee Free Time
#
# https://leetcode.com/problems/employee-free-time/description/
#
# algorithms
# Hard (72.96%)
# Likes:    1972
# Dislikes: 149
# Total Accepted:    183.7K
# Total Submissions: 251.8K
# Testcase Example:  "[[[1,2],[5,6]],[[1,3]],[[4,10]]]"
#
#
# We are given a list schedule of employees, which represents the working
# time for each employee.
#
#
#
# Each employee has a list of non-overlapping Intervals, and these
# intervals are in sorted order.
#
#
#
# Return the list of finite intervals representing common, positive-length
# free time for all employees, also in sorted order.
#
#
#
# (Even though we are representing Intervals in the form [x, y], the
# objects inside are Intervals, not lists or arrays. For example,
# schedule[0][0].start = 1, schedule[0][0].end = 2, and schedule[0][0][0]
# is not defined).  Also, we wouldn't include intervals like [5, 5] in our
# answer, as they have zero length.
#
#
# Example 1:
#
# Input: schedule = [[[1,2],[5,6]],[[1,3]],[[4,10]]]
# Output: [[3,4]]
# Explanation: There are a total of three employees, and all common
# free time intervals would be [-inf, 1], [3, 4], [10, inf].
# We discard any intervals that contain inf as they aren't finite.
#
# Example 2:
#
# Input: schedule = [[[1,3],[6,7]],[[2,4]],[[2,5],[9,12]]]
# Output: [[5,6],[7,9]]
#
# Constraints:
#
# 1 <= schedule.length , schedule[i].length <= 50
#
# 0 <= schedule[i].start < schedule[i].end <= 10^8
#
# @lc code=start
from typing import List

# Definition for an Interval.
class Interval:
    def __init__(self, start: int = None, end: int = None):
        """
        Interview explanation:
        LeetCode interval node for busy/free time ranges.

        Algorithm:
        - Store inclusive-exclusive [start, end) style bounds as given.

        Complexity: O(1).
        """
        self.start = start
        self.end = end


class Solution:
    def employeeFreeTime(self, schedule: List[List[Interval]]) -> List[Interval]:
        """
        Interview explanation:
        Premium. Free time is gaps in the merged union of all employees' busy
        intervals. Flatten all intervals, sort by start, merge overlaps, then
        emit gaps between consecutive merged busy blocks.

        Algorithm:
        - Flatten; sort by start
        - Merge: cur_end = first.end; for each next: if start > cur_end: gap;
          else cur_end = max(cur_end, end)
        - Return list of Interval gaps

        Complexity: O(N log N) time for N total intervals; O(N) space.
        """
        intervals = [iv for emp in schedule for iv in emp]
        intervals.sort(key=lambda x: x.start)
        ans: List[Interval] = []
        cur_end = intervals[0].end
        for iv in intervals[1:]:
            if iv.start > cur_end:
                ans.append(Interval(cur_end, iv.start))
                cur_end = iv.end
            else:
                cur_end = max(cur_end, iv.end)
        return ans
# @lc code=end

