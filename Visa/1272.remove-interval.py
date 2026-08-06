#
# @lc app=leetcode id=1272 lang=python3
#
# [1272] Remove Interval
#
# https://leetcode.com/problems/remove-interval/description/
#
# algorithms
# Medium (67.33%)
# Likes:    482
# Dislikes: 36
# Total Accepted:    43.1K
# Total Submissions: 64K
# Testcase Example:  "[[0,2],[3,4],[5,7]]\n[1,6]"
#
#
# A set of real numbers can be represented as the union of several
# disjoint intervals, where each interval is in the form [a, b). A real
# number x is in the set if one of its intervals [a, b) contains x (i.e. a
# <= x < b).
#
# You are given a sorted list of disjoint intervals intervals representing
# a set of real numbers as described above, where intervals[i] = [a_i,
# b_i] represents the interval [a_i, b_i). You are also given another
# interval toBeRemoved.
#
# Return the set of real numbers with the interval toBeRemoved removed
# from intervals. In other words, return the set of real numbers such that
# every x in the set is in intervals but not in toBeRemoved. Your answer
# should be a sorted list of disjoint intervals as described above.
#
# Example 1:
#
# Input: intervals = [[0,2],[3,4],[5,7]], toBeRemoved = [1,6]
# Output: [[0,1],[6,7]]
#
# Example 2:
#
# Input: intervals = [[0,5]], toBeRemoved = [2,3]
# Output: [[0,2],[3,5]]
#
# Example 3:
#
# Input: intervals = [[-5,-4],[-3,-2],[1,2],[3,5],[8,9]], toBeRemoved =
# [-1,4]
# Output: [[-5,-4],[-3,-2],[4,5],[8,9]]
#
# Constraints:
#
# 1 <= intervals.length <= 10^4
#
# -10^9 <= a_i < b_i <= 10^9
#
# @lc code=start

from typing import List


class Solution:
    def removeInterval(
        self, intervals: List[List[int]], toBeRemoved: List[int]
    ) -> List[List[int]]:
        """
        Interview explanation:
        Premium. Disjoint sorted intervals; remove intersection with
        [removeStart, removeEnd). Keep left remnant [a, removeStart) and right
        remnant [removeEnd, b) when they have positive length.

        Algorithm:
        - rs, re = toBeRemoved.
        - For each [a,b]: if b<=rs or a>=re: keep whole; else add [a,rs) if
          a<rs and [re,b) if b>re.

        Complexity: O(n) time, O(n) output space.
        """
        rs, re = toBeRemoved
        ans = []
        for a, b in intervals:
            if b <= rs or a >= re:
                ans.append([a, b])
            else:
                if a < rs:
                    ans.append([a, rs])
                if b > re:
                    ans.append([re, b])
        return ans
# @lc code=end
