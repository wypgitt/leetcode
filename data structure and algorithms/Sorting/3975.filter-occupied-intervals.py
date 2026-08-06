#
# @lc app=leetcode id=3975 lang=python3
#
# [3975] Filter Occupied Intervals
#
# https://leetcode.com/problems/filter-occupied-intervals/description/
#
# algorithms
# Medium (45.93%)
# Likes:    77
# Dislikes: 8
# Total Accepted:    29.6K
# Total Submissions: 64.5K
# Testcase Example:  "[[2,6],[4,8],[10,10],[10,12],[14,16]]\n7\n11"
#
#
# You are given a 2D integer array occupiedIntervals, where
# occupiedIntervals[i] = [start_i, end_i] represents a time interval
# during which you are occupied. Each interval starts at start_i and ends
# at end_i, inclusive. These intervals may overlap.
#
# You are also given two integers freeStart and freeEnd, which define a
# free time interval from freeStart to freeEnd, inclusive.
#
# Your task is to merge all occupied intervals that overlap or touch, then
# remove all integer points in the free interval from the merged occupied
# intervals.
#
# Two intervals touch if the second interval starts immediately after the
# first one ends. For example, [1, 1] and [2, 2] touch and should be
# merged into [1, 2].
#
# Return the remaining occupied intervals in sorted order. The returned
# intervals must be non-overlapping and must contain the minimum number of
# intervals possible. If there are no remaining occupied points, return an
# empty list.
#
# Example 1:
#
# Input: occupiedIntervals = [[2,6],[4,8],[10,10],[10,12],[14,16]],
# freeStart = 7, freeEnd = 11
#
# Output: [[2,6],[12,12],[14,16]]
#
# Explanation:
#
# After merging, the occupied intervals are [2, 8], [10, 12], and [14,
# 16].
#
# Excluding the free interval [7, 11] results in [2, 6], [12, 12], and
# [14, 16].
#
# Example 2:
#
# Input: occupiedIntervals = [[1,5],[2,3]], freeStart = 3, freeEnd = 8
#
# Output: [[1,2]]
#
# Explanation:
#
# After merging, the occupied interval is [1, 5].
#
# Excluding the free interval [3, 8] results in [1, 2].
#
# Constraints:
#
# 1 <= occupiedIntervals.length <= 5 * 10^4
#
# occupiedIntervals[i].length == 2
#
# 1 <= start_i <= end_i <= 10^9
#
# 1 <= freeStart <= freeEnd <= 10^9
#

# @lc code=start

from typing import List


class Solution:
    def filterOccupiedIntervals(
        self, occupiedIntervals: List[List[int]], freeStart: int, freeEnd: int
    ) -> List[List[int]]:
        """
        Interview explanation:
        Merge touching/overlapping occupied intervals, then cut out the free
        window [freeStart, freeEnd].

        Algorithm:
        - Sort by start and merge intervals that touch or overlap.
        - For each merged interval, keep the part left of freeStart and/or right
          of freeEnd when nonempty.

        Complexity: O(n log n) time, O(n) space.
        """
        occupiedIntervals.sort(key=lambda x: x[0])
        busy = [occupiedIntervals[0][:]]
        for interval in occupiedIntervals[1:]:
            if busy[-1][1] + 1 < interval[0]:
                busy.append(interval[:])
            else:
                busy[-1][1] = max(busy[-1][1], interval[1])
        ans = []
        for interval in busy:
            if interval[1] < freeStart or freeEnd < interval[0]:
                ans.append(interval)
            else:
                if interval[0] < freeStart:
                    ans.append([interval[0], freeStart - 1])
                if interval[1] > freeEnd:
                    ans.append([freeEnd + 1, interval[1]])
        return ans
# @lc code=end
