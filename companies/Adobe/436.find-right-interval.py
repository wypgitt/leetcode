#
# @lc app=leetcode id=436 lang=python3
#
# [436] Find Right Interval
#
# https://leetcode.com/problems/find-right-interval/description/
#
# algorithms
# Medium (55.78%)
# Likes:    2366
# Dislikes: 400
# Total Accepted:    161.8K
# Total Submissions: 290K
# Testcase Example:  '[[1,2]]'
#
# You are given an array of intervals, where intervals[i] = [starti, endi] and
# each starti is unique.
# 
# The right interval for an interval i is an interval j such that startj >=
# endi and startj is minimized. Note that i may equal j.
# 
# Return an array of right interval indices for each interval i. If no right
# interval exists for interval i, then put -1 at index i.
# 
# 
# Example 1:
# 
# 
# Input: intervals = [[1,2]]
# Output: [-1]
# Explanation: There is only one interval in the collection, so it outputs
# -1.
# 
# 
# Example 2:
# 
# 
# Input: intervals = [[3,4],[2,3],[1,2]]
# Output: [-1,0,1]
# Explanation: There is no right interval for [3,4].
# The right interval for [2,3] is [3,4] since start0 = 3 is the smallest start
# that is >= end1 = 3.
# The right interval for [1,2] is [2,3] since start1 = 2 is the smallest start
# that is >= end2 = 2.
# 
# 
# Example 3:
# 
# 
# Input: intervals = [[1,4],[2,3],[3,4]]
# Output: [-1,2,-1]
# Explanation: There is no right interval for [1,4] and [3,4].
# The right interval for [2,3] is [3,4] since start2 = 3 is the smallest start
# that is >= end1 = 3.
# 
# 
# 
# Constraints:
# 
# 
# 1 <= intervals.length <= 2 * 10^4
# intervals[i].length == 2
# -10^6 <= starti <= endi <= 10^6
# The start point of each interval is unique.
# 
# 
#

# @lc code=start
from bisect import bisect_left
from typing import List


class Solution:
    def findRightInterval(self, intervals: List[List[int]]) -> List[int]:
        starts = sorted((start, i) for i, (start, _) in enumerate(intervals))
        ans = []
        for _, end in intervals:
            pos = bisect_left(starts, (end, -1))
            ans.append(starts[pos][1] if pos < len(starts) else -1)
        return ans
# @lc code=end

"""
Interview explanation:
For each interval, we need the interval with the smallest start >= current end. Sorting all starts turns the query into a lower_bound/binary-search operation.

Data structure: store pairs (start, original_index) so sorting keeps enough information to return the original index.

Edge cases: if no start is large enough, return -1. Intervals have unique starts in the original problem, but using pairs is still robust.

Complexity: sorting costs O(n log n), and n binary searches cost O(n log n). Space is O(n) for the sorted starts and answer.
"""
