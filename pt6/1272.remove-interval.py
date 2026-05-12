#
# @lc app=leetcode id=1272 lang=python3
#
# [1272] Remove Interval
#
# https://leetcode.com/problems/remove-interval/description/
#
# algorithms
# Medium (67.22%)
# Likes:    480
# Dislikes: 36
# Total Accepted:    42.6K
# Total Submissions: 63.3K
# Testcase Example:  '[[0,2],[3,4],[5,7]]\n[1,6]'
#
# A set of real numbers can be represented as the union of several disjoint
# intervals, where each interval is in the form [a, b). A real number x is in
# the set if one of its intervals [a, b) contains x (i.e. a <= x < b).
# 
# You are given a sorted list of disjoint intervals intervals representing a
# set of real numbers as described above, where intervals[i] = [ai, bi]
# represents the interval [ai, bi). You are also given another interval
# toBeRemoved.
# 
# Return the set of real numbers with the interval toBeRemoved removed from
# intervals. In other words, return the set of real numbers such that every x
# in the set is in intervals but not in toBeRemoved. Your answer should be a
# sorted list of disjoint intervals as described above.
# 
# 
# Example 1:
# 
# 
# Input: intervals = [[0,2],[3,4],[5,7]], toBeRemoved = [1,6]
# Output: [[0,1],[6,7]]
# 
# 
# Example 2:
# 
# 
# Input: intervals = [[0,5]], toBeRemoved = [2,3]
# Output: [[0,2],[3,5]]
# 
# 
# Example 3:
# 
# 
# Input: intervals = [[-5,-4],[-3,-2],[1,2],[3,5],[8,9]], toBeRemoved = [-1,4]
# Output: [[-5,-4],[-3,-2],[4,5],[8,9]]
# 
# 
# 
# Constraints:
# 
# 
# 1 <= intervals.length <= 10^4
# -10^9 <= ai < bi <= 10^9
# 
# 
#

# @lc code=start
from typing import List


class Solution:
    def removeInterval(self, intervals: List[List[int]], toBeRemoved: List[int]) -> List[List[int]]:
        remove_start, remove_end = toBeRemoved
        remaining = []

        for start, end in intervals:
            if end <= remove_start or start >= remove_end:
                remaining.append([start, end])
                continue

            if start < remove_start:
                remaining.append([start, remove_start])
            if remove_end < end:
                remaining.append([remove_end, end])

        return remaining
# @lc code=end

# Explanation
# -----------
# For each interval, compare it with the interval to remove. If there is no
# overlap, keep it unchanged. If there is overlap, at most two pieces can
# survive: the part before remove_start and the part after remove_end.
#
# This direct interval-splitting approach is best because input intervals are
# already disjoint and sorted by the problem constraints. No merging structure
# is needed.
#
# Edge cases: removal cuts the middle of an interval; removal covers an entire
# interval; removal touches an endpoint, where zero-length pieces must not be
# emitted.
#
# Time complexity: O(n).
# Space complexity: O(n) for the returned intervals.
