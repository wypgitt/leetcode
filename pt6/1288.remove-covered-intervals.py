#
# @lc app=leetcode id=1288 lang=python3
#
# [1288] Remove Covered Intervals
#
# https://leetcode.com/problems/remove-covered-intervals/description/
#
# algorithms
# Medium (56.08%)
# Likes:    2316
# Dislikes: 61
# Total Accepted:    143.9K
# Total Submissions: 256.6K
# Testcase Example:  '[[1,4],[3,6],[2,8]]'
#
# Given an array intervals where intervals[i] = [li, ri] represent the interval
# [li, ri), remove all intervals that are covered by another interval in the
# list.
# 
# The interval [a, b) is covered by the interval [c, d) if and only if c <= a
# and b <= d.
# 
# Return the number of remaining intervals.
# 
# 
# Example 1:
# 
# 
# Input: intervals = [[1,4],[3,6],[2,8]]
# Output: 2
# Explanation: Interval [3,6] is covered by [2,8], therefore it is removed.
# 
# 
# Example 2:
# 
# 
# Input: intervals = [[1,4],[2,3]]
# Output: 1
# 
# 
# 
# Constraints:
# 
# 
# 1 <= intervals.length <= 1000
# intervals[i].length == 2
# 0 <= li < ri <= 10^5
# All the given intervals are unique.
# 
# 
#

# @lc code=start
from typing import List


class Solution:
    def removeCoveredIntervals(self, intervals: List[List[int]]) -> int:
        intervals.sort(key=lambda interval: (interval[0], -interval[1]))
        remaining = 0
        farthest_end = 0

        for _, end in intervals:
            if end > farthest_end:
                remaining += 1
                farthest_end = end

        return remaining
# @lc code=end

# Explanation
# -----------
# Sort intervals by start ascending and end descending. With that order, if an
# interval's end is <= the farthest end seen so far, it is covered by an
# earlier interval. Otherwise it is not covered and extends the farthest end.
#
# Sorting end descending for equal starts is important: [1, 4] must appear
# before [1, 3] so the shorter interval is recognized as covered.
#
# Edge cases: same starting point; disjoint intervals; partially overlapping
# intervals that are not fully covered.
#
# Time complexity: O(n log n).
# Space complexity: O(1) besides sorting overhead.
