#
# @lc app=leetcode id=1893 lang=python3
#
# [1893] Check if All the Integers in a Range Are Covered
#
# https://leetcode.com/problems/check-if-all-the-integers-in-a-range-are-covered/description/
#
# algorithms
# Easy (51.24%)
# Likes:    685
# Dislikes: 127
# Total Accepted:    71.7K
# Total Submissions: 140K
# Testcase Example:  "[[1,2],[3,4],[5,6]]"
#
# You are given a 2D integer array ranges and two integers left and right. Each
# ranges[i] = [start_i, end_i] represents an inclusive interval between start_i
# and end_i.
#
# Return true if each integer in the inclusive range [left, right] is covered
# by at least one interval in ranges. Return false otherwise.
#
# An integer x is covered by an interval ranges[i] = [start_i, end_i] if
# start_i <= x <= end_i.
#
# Example 1:
#
# Input: ranges = [[1,2],[3,4],[5,6]], left = 2, right = 5
# Output: true
# Explanation: Every integer between 2 and 5 is covered:
# - 2 is covered by the first range.
# - 3 and 4 are covered by the second range.
# - 5 is covered by the third range.
#
# Example 2:
#
# Input: ranges = [[1,10],[10,20]], left = 21, right = 21
# Output: false
# Explanation: 21 is not covered by any range.
#
# Constraints:
#
# 1 <= ranges.length <= 50
#
# 1 <= start_i <= end_i <= 50
#
# 1 <= left <= right <= 50
#

# @lc code=start
from typing import List


class Solution:
    def isCovered(self, ranges: List[List[int]], left: int, right: int) -> bool:
        """
        Interview explanation:
        Check every integer in [left,right] lies in some ranges[i]=[start,end].

        Algorithm (diff array over 1..50):
        - diff[s]++, diff[e+1]--; prefix; verify coverage on [left,right].

        Complexity: O(n + R) time with R≤50, O(R) space.
        """
        diff = [0] * 52
        for s, e in ranges:
            diff[s] += 1
            diff[e + 1] -= 1
        cur = 0
        for x in range(1, 51):
            cur += diff[x]
            if left <= x <= right and cur <= 0:
                return False
        return True

    def isCovered_scan(self, ranges: List[List[int]], left: int, right: int) -> bool:
        """
        Interview explanation:
        Alternate: for each x in [left,right] scan ranges for coverage.

        Algorithm:
        - all(any(s<=x<=e for s,e in ranges) for x in range(left,right+1)).

        Complexity: O((right-left)*n) time.
        """
        for x in range(left, right + 1):
            if not any(s <= x <= e for s, e in ranges):
                return False
        return True
# @lc code=end
