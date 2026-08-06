#
# @lc app=leetcode id=3169 lang=python3
#
# [3169] Count Days Without Meetings
#
# https://leetcode.com/problems/count-days-without-meetings/description/
#
# algorithms
# Medium (48.19%)
# Likes:    797
# Dislikes: 20
# Total Accepted:    186.5K
# Total Submissions: 386.9K
# Testcase Example:  "10\n[[5,7],[1,3],[9,10]]"
#
#
# You are given a positive integer days representing the total number of
# days an employee is available for work (starting from day 1). You are
# also given a 2D array meetings of size n where, meetings[i] = [start_i,
# end_i] represents the starting and ending days of meeting i (inclusive).
#
# Return the count of days when the employee is available for work but no
# meetings are scheduled.
#
# Note: The meetings may overlap.
#
# Example 1:
#
# Input: days = 10, meetings = [[5,7],[1,3],[9,10]]
#
# Output: 2
#
# Explanation:
#
# There is no meeting scheduled on the 4^th and 8^th days.
#
# Example 2:
#
# Input: days = 5, meetings = [[2,4],[1,3]]
#
# Output: 1
#
# Explanation:
#
# There is no meeting scheduled on the 5^th day.
#
# Example 3:
#
# Input: days = 6, meetings = [[1,6]]
#
# Output: 0
#
# Explanation:
#
# Meetings are scheduled for all working days.
#
# Constraints:
#
# 1 <= days <= 10^9
#
# 1 <= meetings.length <= 10^5
#
# meetings[i].length == 2
#
# 1 <= meetings[i][0] <= meetings[i][1] <= days
#

# @lc code=start
from typing import List


class Solution:
    def countDays(self, days: int, meetings: List[List[int]]) -> int:
        """
        Interview explanation:
        days can be 1e9, so we cannot mark a boolean array. Free days = total
        minus the measure of the union of meeting intervals.

        Algorithm:
        - Sort meetings by start; merge overlaps while scanning; subtract covered
          length from days (or accumulate gaps).

        Complexity: O(m log m) time, O(1) extra space.
        """
        meetings.sort()
        free = 0
        prev_end = 0
        for start, end in meetings:
            if start > prev_end + 1:
                free += start - prev_end - 1
            prev_end = max(prev_end, end)
        free += days - prev_end
        return free

    def countDays_union(self, days: int, meetings: List[List[int]]) -> int:
        """
        Interview explanation:
        Alternate: compute union length of meetings, return days - covered.

        Algorithm:
        - Sort and merge; sum merged lengths; subtract from days.

        Complexity: O(m log m) time, O(1) space.
        """
        meetings.sort()
        covered = 0
        cur_s = cur_e = -1
        for start, end in meetings:
            if cur_s < 0 or start > cur_e + 1:
                if cur_s >= 0:
                    covered += cur_e - cur_s + 1
                cur_s, cur_e = start, end
            else:
                cur_e = max(cur_e, end)
        if cur_s >= 0:
            covered += cur_e - cur_s + 1
        return days - covered
# @lc code=end
