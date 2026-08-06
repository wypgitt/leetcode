#
# @lc app=leetcode id=435 lang=python3
#
# [435] Non-overlapping Intervals
#
# https://leetcode.com/problems/non-overlapping-intervals/description/
#
# algorithms
# Medium (57.51%)
# Likes:    9286
# Dislikes: 262
# Total Accepted:    1.1M
# Total Submissions: 1.9M
# Testcase Example:  "[[1,2],[2,3],[3,4],[1,3]]"
#
# Given an array of intervals intervals where intervals[i] = [start_i, end_i],
# return the minimum number of intervals you need to remove to make the rest of
# the intervals non-overlapping.
#
# Note that intervals which only touch at a point are non-overlapping. For
# example, [1, 2] and [2, 3] are non-overlapping.
#
# Example 1:
#
# Input: intervals = [[1,2],[2,3],[3,4],[1,3]]
# Output: 1
# Explanation: [1,3] can be removed and the rest of the intervals are
# non-overlapping.
#
# Example 2:
#
# Input: intervals = [[1,2],[1,2],[1,2]]
# Output: 2
# Explanation: You need to remove two [1,2] to make the rest of the intervals
# non-overlapping.
#
# Example 3:
#
# Input: intervals = [[1,2],[2,3]]
# Output: 0
# Explanation: You don't need to remove any of the intervals since they're
# already non-overlapping.
#
# Constraints:
#
# 1 <= intervals.length <= 10^5
#
# intervals[i].length == 2
#
# -5 * 10^4 <= start_i < end_i <= 5 * 10^4
#

# @lc code=start

from typing import List


class Solution:
    def eraseOverlapIntervals(self, intervals: List[List[int]]) -> int:
        """
        Interview explanation:
        Greedy: sort by end time; keep intervals that start >= last kept end;
        count how many are discarded. Equivalent to maximizing non-overlapping set.

        Algorithm:
        - Sort by end ascending.
        - end = -inf; removed=0; for each interval: if start < end: removed++;
          else end = interval end.

        Complexity: O(n log n) time, O(1)/O(n) space depending on sort.
        """
        if not intervals:
            return 0
        intervals.sort(key=lambda x: x[1])
        end = float("-inf")
        removed = 0
        for s, e in intervals:
            if s < end:
                removed += 1
            else:
                end = e
        return removed
# @lc code=end
