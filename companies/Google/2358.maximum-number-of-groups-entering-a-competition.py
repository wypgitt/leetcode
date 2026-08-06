#
# @lc app=leetcode id=2358 lang=python3
#
# [2358] Maximum Number of Groups Entering a Competition
#
# https://leetcode.com/problems/maximum-number-of-groups-entering-a-competition/description/
#
# algorithms
# Medium (68.65%)
# Likes:    716
# Dislikes: 122
# Total Accepted:    46.2K
# Total Submissions: 67.2K
# Testcase Example:  "[10,6,12,7,3,5]"
#
# You are given a positive integer array grades which represents the grades of
# students in a university. You would like to enter all these students into a
# competition in ordered non-empty groups, such that the ordering meets the
# following conditions:
#
#
# The sum of the grades of students in the i^th group is less than the sum of
# the grades of students in the (i + 1)^th group, for all groups (except the
# last).
#
#
# The total number of students in the i^th group is less than the total number
# of students in the (i + 1)^th group, for all groups (except the last).
#
# Return the maximum number of groups that can be formed.
#
#
#
# Example 1:
#
# Input: grades = [10,6,12,7,3,5]
# Output: 3
# Explanation: The following is a possible way to form 3 groups of students:
# - 1^st group has the students with grades = [12]. Sum of grades: 12. Student
# count: 1
# - 2^nd group has the students with grades = [6,7]. Sum of grades: 6 + 7 = 13.
# Student count: 2
# - 3^rd group has the students with grades = [10,3,5]. Sum of grades: 10 + 3 +
# 5 = 18. Student count: 3
# It can be shown that it is not possible to form more than 3 groups.
#
# Example 2:
#
# Input: grades = [8,8]
# Output: 1
# Explanation: We can only form 1 group, since forming 2 groups would lead to an
# equal number of students in both groups.
#
#
#
# Constraints:
#
#
# 1 <= grades.length <= 10^5
#
#
# 1 <= grades[i] <= 10^5
#

# @lc code=start

from typing import List
import math


class Solution:
    def maximumGroups(self, grades: List[int]) -> int:
        """
        Interview explanation:
        Split into max groups where group i has more students and strictly
        larger total grade than group i-1. Optimal: sizes 1,2,3,... so only
        count matters: max k with k(k+1)/2 <= n.

        Algorithm:
        - Math: largest k with k(k+1)/2 <= n via formula or binary search.

        Complexity: O(1) time, O(1) space.
        """
        n = len(grades)
        # k ~= (-1 + sqrt(1+8n)) / 2
        return int((-1 + math.isqrt(1 + 8 * n)) // 2)

    def maximumGroups_binary_search(self, grades: List[int]) -> int:
        """
        Interview explanation:
        Alternate: binary search max k with triangular number <= n.

        Algorithm:
        - lo/hi on k; check mid*(mid+1)//2 <= n.

        Complexity: O(log n) time, O(1) space.
        """
        n = len(grades)
        lo, hi = 1, n
        while lo < hi:
            mid = (lo + hi + 1) // 2
            if mid * (mid + 1) // 2 <= n:
                lo = mid
            else:
                hi = mid - 1
        return lo
# @lc code=end
