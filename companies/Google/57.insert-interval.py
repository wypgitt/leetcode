#
# @lc app=leetcode id=57 lang=python3
#
# [57] Insert Interval
#
# https://leetcode.com/problems/insert-interval/description/
#
# algorithms
# Medium (45.15%)
# Likes:    11882
# Dislikes: 922
# Total Accepted:    1.8M
# Total Submissions: 3.9M
# Testcase Example:  '[[1,3],[6,9]]\n[2,5]'
#
# You are given an array of non-overlapping intervals intervals where
# intervals[i] = [starti, endi] represent the start and the end of the i^th
# interval and intervals is sorted in ascending order by starti. You are also
# given an interval newInterval = [start, end] that represents the start and
# end of another interval.
# 
# Insert newInterval into intervals such that intervals is still sorted in
# ascending order by starti and intervals still does not have any overlapping
# intervals (merge overlapping intervals if necessary).
# 
# Return intervals after the insertion.
# 
# Note that you don't need to modify intervals in-place. You can make a new
# array and return it.
# 
# 
# Example 1:
# 
# 
# Input: intervals = [[1,3],[6,9]], newInterval = [2,5]
# Output: [[1,5],[6,9]]
# 
# 
# Example 2:
# 
# 
# Input: intervals = [[1,2],[3,5],[6,7],[8,10],[12,16]], newInterval = [4,8]
# Output: [[1,2],[3,10],[12,16]]
# Explanation: Because the new interval [4,8] overlaps with
# [3,5],[6,7],[8,10].
# 
# 
# 
# Constraints:
# 
# 
# 0 <= intervals.length <= 10^4
# intervals[i].length == 2
# 0 <= starti <= endi <= 10^5
# intervals is sorted by starti in ascending order.
# newInterval.length == 2
# 0 <= start <= end <= 10^5
# 
# 
#

# @lc code=start
from typing import List, Optional
class Solution:
    def insert(self, intervals: List[List[int]], newInterval: List[int]) -> List[List[int]]:
        """
        Interview explanation:
        The existing intervals are already sorted and non-overlapping. Split the
        scan into three phases: intervals ending before newInterval, intervals
        overlapping newInterval, and intervals starting after it. Only the middle
        phase changes the new interval boundaries.

        Edge cases and tests:
        - Insert before all intervals or after all intervals.
        - Merge with one or many intervals.
        - Empty intervals list returns [newInterval].

        Complexity: O(n) time, O(n) output space.
        """
        ans = []
        i = 0
        n = len(intervals)
        start, end = newInterval

        while i < n and intervals[i][1] < start:
            ans.append(intervals[i])
            i += 1

        while i < n and intervals[i][0] <= end:
            start = min(start, intervals[i][0])
            end = max(end, intervals[i][1])
            i += 1
        ans.append([start, end])

        while i < n:
            ans.append(intervals[i])
            i += 1

        return ans
# @lc code=end


