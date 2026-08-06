#
# @lc app=leetcode id=2580 lang=python3
#
# [2580] Count Ways to Group Overlapping Ranges
#
# https://leetcode.com/problems/count-ways-to-group-overlapping-ranges/description/
#
# algorithms
# Medium (39.41%)
# Likes:    344
# Dislikes: 27
# Total Accepted:    24.9K
# Total Submissions: 63.2K
# Testcase Example:  "[[6,10],[5,15]]"
#
# You are given a 2D integer array ranges where ranges[i] = [start_i, end_i]
# denotes that all integers between start_i and end_i (both inclusive) are
# contained in the i^th range.
#
# You are to split ranges into two (possibly empty) groups such that:
#
#
# Each range belongs to exactly one group.
#
#
# Any two overlapping ranges must belong to the same group.
#
# Two ranges are said to be overlapping if there exists at least one integer
# that is present in both ranges.
#
#
# For example, [1, 3] and [2, 5] are overlapping because 2 and 3 occur in both
# ranges.
#
# Return the total number of ways to split ranges into two groups. Since the
# answer may be very large, return it modulo 10^9 + 7.
#
#
#
# Example 1:
#
# Input: ranges = [[6,10],[5,15]]
# Output: 2
# Explanation:
# The two ranges are overlapping, so they must be in the same group.
# Thus, there are two possible ways:
# - Put both the ranges together in group 1.
# - Put both the ranges together in group 2.
#
# Example 2:
#
# Input: ranges = [[1,3],[10,20],[2,5],[4,8]]
# Output: 4
# Explanation:
# Ranges [1,3], and [2,5] are overlapping. So, they must be in the same group.
# Again, ranges [2,5] and [4,8] are also overlapping. So, they must also be in
# the same group.
# Thus, there are four possible ways to group them:
# - All the ranges in group 1.
# - All the ranges in group 2.
# - Ranges [1,3], [2,5], and [4,8] in group 1 and [10,20] in group 2.
# - Ranges [1,3], [2,5], and [4,8] in group 2 and [10,20] in group 1.
#
#
#
# Constraints:
#
#
# 1 <= ranges.length <= 10^5
#
#
# ranges[i].length == 2
#
#
# 0 <= start_i <= end_i <= 10^9
#

# @lc code=start
from typing import List


class Solution:
    def countWays(self, ranges: List[List[int]]) -> int:
        """
        Interview explanation:
        Ranges that overlap (transitively) must stay in the same group. Count ways to
        assign each connected component to one of two groups: 2^{components}.

        Algorithm:
        - Sort by start; merge overlapping intervals; answer pow(2, comps, MOD).

        Complexity: O(n log n) time, O(n) space.
        """
        MOD = 10**9 + 7
        ranges.sort()
        comps = 0
        cur_end = -1
        for s, e in ranges:
            if s > cur_end:
                comps += 1
                cur_end = e
            else:
                cur_end = max(cur_end, e)
        return pow(2, comps, MOD)
# @lc code=end
