#
# @lc app=leetcode id=56 lang=python3
#
# [56] Merge Intervals
#
# https://leetcode.com/problems/merge-intervals/description/
#
# algorithms
# Medium (51.73%)
# Likes:    24691
# Dislikes: 908
# Total Accepted:    4M
# Total Submissions: 7.7M
# Testcase Example:  '[[1,3],[2,6],[8,10],[15,18]]'
#
# Given an array of intervals where intervals[i] = [starti, endi], merge all
# overlapping intervals, and return an array of the non-overlapping intervals
# that cover all the intervals in the input.
# 
# 
# Example 1:
# 
# 
# Input: intervals = [[1,3],[2,6],[8,10],[15,18]]
# Output: [[1,6],[8,10],[15,18]]
# Explanation: Since intervals [1,3] and [2,6] overlap, merge them into
# [1,6].
# 
# 
# Example 2:
# 
# 
# Input: intervals = [[1,4],[4,5]]
# Output: [[1,5]]
# Explanation: Intervals [1,4] and [4,5] are considered overlapping.
# 
# 
# Example 3:
# 
# 
# Input: intervals = [[4,7],[1,4]]
# Output: [[1,7]]
# Explanation: Intervals [1,4] and [4,7] are considered overlapping.
# 
# 
# 
# Constraints:
# 
# 
# 1 <= intervals.length <= 10^4
# intervals[i].length == 2
# 0 <= starti <= endi <= 10^4
# 
# 
#

# @lc code=start
from typing import List, Optional
class Solution:
    def merge(self, intervals: List[List[int]]) -> List[List[int]]:
        """
        Interview explanation:
        Sort intervals by start. Once sorted, any interval that overlaps the
        current merged interval must appear immediately after it; non-overlap
        means the current merged interval is complete.

        Edge cases and tests:
        - Touching intervals like [1,4] and [4,5] merge.
        - Fully contained intervals do not extend the end.
        - One interval returns unchanged.

        Complexity: O(n log n) time for sorting, O(n) output space.
        """
        intervals.sort(key=lambda x: x[0])
        merged = []

        for start, end in intervals:
            if not merged or start > merged[-1][1]:
                merged.append([start, end])
            else:
                merged[-1][1] = max(merged[-1][1], end)

        return merged
# @lc code=end


