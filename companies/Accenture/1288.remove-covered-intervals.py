#
# @lc app=leetcode id=1288 lang=python3
#
# [1288] Remove Covered Intervals
#
# https://leetcode.com/problems/remove-covered-intervals/description/
#
# algorithms
# Medium (60.14%)
# Likes:    2607
# Dislikes: 70
# Total Accepted:    266K
# Total Submissions: 442K
# Testcase Example:  "[[52141,92589],[52991,93486],[46321,59199],[51955,78788],[18533,23127]]"
#
# Given an array intervals where intervals[i] = [l_i, r_i] represent the
# interval [l_i, r_i), remove all intervals that are covered by another
# interval in the list.
#
# The interval [a, b) is covered by the interval [c, d) if and only if c <= a
# and b <= d.
#
# Return the number of remaining intervals.
#
# Example 1:
#
# Input: intervals = [[1,4],[3,6],[2,8]]
# Output: 2
# Explanation: Interval [3,6] is covered by [2,8], therefore it is removed.
#
# Example 2:
#
# Input: intervals = [[1,4],[2,3]]
# Output: 1
#
# Constraints:
#
# 1 <= intervals.length <= 1000
#
# intervals[i].length == 2
#
# 0 <= l_i < r_i <= 10^5
#
# All the given intervals are unique.
#

# @lc code=start

from typing import List


class Solution:
    def removeCoveredIntervals(self, intervals: List[List[int]]) -> int:
        """
        Interview explanation:
        Interval A covers B if a1<=b1 and b2<=a2. Sort by start asc, end desc
        so earlier intervals are likelier covers; track max end seen; skip if
        cur end <= max_end (covered).

        Algorithm:
        - Sort key=(start, -end).
        - max_end=-1; count=0; for each: if end>max_end: count++; max_end=end.
        - Return count.

        Complexity: O(n log n) time, O(1)/O(n) sort space.
        """
        intervals.sort(key=lambda x: (x[0], -x[1]))
        count = 0
        max_end = -1
        for _, end in intervals:
            if end > max_end:
                count += 1
                max_end = end
        return count
# @lc code=end
