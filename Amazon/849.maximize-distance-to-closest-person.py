#
# @lc app=leetcode id=849 lang=python3
#
# [849] Maximize Distance to Closest Person
#
# https://leetcode.com/problems/maximize-distance-to-closest-person/description/
#
# algorithms
# Medium (49.93%)
# Likes:    3354
# Dislikes: 202
# Total Accepted:    292K
# Total Submissions: 585K
# Testcase Example:  "[1,0,0,0,1,0,1]"
#
# You are given an array representing a row of seats where seats[i] = 1
# represents a person sitting in the i^th seat, and seats[i] = 0 represents
# that the i^th seat is empty (0-indexed).
#
# There is at least one empty seat, and at least one person sitting.
#
# Alex wants to sit in the seat such that the distance between him and the
# closest person to him is maximized.
#
# Return that maximum distance to the closest person.
#
# Example 1:
#
# Input: seats = [1,0,0,0,1,0,1]
# Output: 2
# Explanation:
# If Alex sits in the second open seat (i.e. seats[2]), then the closest person
# has distance 2.
# If Alex sits in any other open seat, the closest person has distance 1.
# Thus, the maximum distance to the closest person is 2.
#
# Example 2:
#
# Input: seats = [1,0,0,0]
# Output: 3
# Explanation:
# If Alex sits in the last seat (i.e. seats[3]), the closest person is 3 seats
# away.
# This is the maximum distance possible, so the answer is 3.
#
# Example 3:
#
# Input: seats = [0,1]
# Output: 1
#
# Constraints:
#
# 2 <= seats.length <= 2 * 10^4
#
# seats[i] is 0 or 1.
#
# At least one seat is empty.
#
# At least one seat is occupied.
#

# @lc code=start

from typing import List


class Solution:
    def maxDistToClosest(self, seats: List[int]) -> int:
        """
        Interview explanation:
        Sit in empty seat maximizing min distance to nearest person. Edges:
        first/last empty runs; middle: half the gap between two occupied seats.

        Algorithm:
        - Track previous occupied index; update max for gaps and edges.

        Complexity: O(n) time, O(1) space.
        """
        n = len(seats)
        prev = -1
        ans = 0
        for i, s in enumerate(seats):
            if s == 1:
                if prev == -1:
                    ans = max(ans, i)  # leading empties
                else:
                    ans = max(ans, (i - prev) // 2)
                prev = i
        ans = max(ans, n - 1 - prev)  # trailing
        return ans

    def maxDistToClosest_two_pass(self, seats: List[int]) -> int:
        """
        Interview explanation:
        Two-pass distances to nearest person left and right; answer is max of
        min(left,right) over empty seats.

        Algorithm:
        - left[i], right[i] nearest 1; max min over zeros.

        Complexity: O(n) time, O(n) space.
        """
        n = len(seats)
        left = [n] * n
        right = [n] * n
        for i in range(n):
            if seats[i] == 1:
                left[i] = 0
            elif i:
                left[i] = left[i - 1] + 1
        for i in range(n - 1, -1, -1):
            if seats[i] == 1:
                right[i] = 0
            elif i < n - 1:
                right[i] = right[i + 1] + 1
        return max(min(left[i], right[i]) for i in range(n) if seats[i] == 0)
# @lc code=end
