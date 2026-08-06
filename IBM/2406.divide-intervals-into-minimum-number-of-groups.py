#
# @lc app=leetcode id=2406 lang=python3
#
# [2406] Divide Intervals Into Minimum Number of Groups
#
# https://leetcode.com/problems/divide-intervals-into-minimum-number-of-groups/description/
#
# algorithms
# Medium (63.59%)
# Likes:    1486
# Dislikes: 43
# Total Accepted:    146.6K
# Total Submissions: 230.6K
# Testcase Example:  "[[5,10],[6,8],[1,5],[2,3],[1,10]]"
#
# You are given a 2D integer array intervals where intervals[i] = [left_i,
# right_i] represents the inclusive interval [left_i, right_i].
#
# You have to divide the intervals into one or more groups such that each
# interval is in exactly one group, and no two intervals that are in the same
# group intersect each other.
#
# Return the minimum number of groups you need to make.
#
# Two intervals intersect if there is at least one common number between them.
# For example, the intervals [1, 5] and [5, 8] intersect.
#
#
#
# Example 1:
#
# Input: intervals = [[5,10],[6,8],[1,5],[2,3],[1,10]]
# Output: 3
# Explanation: We can divide the intervals into the following groups:
# - Group 1: [1, 5], [6, 8].
# - Group 2: [2, 3], [5, 10].
# - Group 3: [1, 10].
# It can be proven that it is not possible to divide the intervals into fewer
# than 3 groups.
#
# Example 2:
#
# Input: intervals = [[1,3],[5,6],[8,10],[11,13]]
# Output: 1
# Explanation: None of the intervals overlap, so we can put all of them in one
# group.
#
#
#
# Constraints:
#
#
# 1 <= intervals.length <= 10^5
#
#
# intervals[i].length == 2
#
#
# 1 <= left_i <= right_i <= 10^6
#

# @lc code=start
from typing import List
import heapq


class Solution:
    def minGroups(self, intervals: List[List[int]]) -> int:
        """
        Interview explanation:
        Split intervals into min groups where no two intervals in a group overlap
        (inclusive endpoints). Equivalent to max concurrent overlap.

        Algorithm:
        - Sort by start; min-heap of group end times; assign to earliest ending
          group if free, else new group. Answer = heap size max / final size.

        Complexity: O(n log n) time, O(n) space.
        """
        intervals.sort()
        ends: List[int] = []
        for s, e in intervals:
            if ends and ends[0] < s:
                heapq.heappop(ends)
            heapq.heappush(ends, e)
        return len(ends)

    def minGroups_sweep(self, intervals: List[List[int]]) -> int:
        """
        Interview explanation:
        Alternate sweep-line: max number of open intervals at once.

        Algorithm:
        - +1 at start, -1 at end+1; scan sorted events for peak.

        Complexity: O(n log n) time, O(n) space.
        """
        events = []
        for s, e in intervals:
            events.append((s, 1))
            events.append((e + 1, -1))
        events.sort()
        cur = ans = 0
        for _, d in events:
            cur += d
            ans = max(ans, cur)
        return ans
# @lc code=end
