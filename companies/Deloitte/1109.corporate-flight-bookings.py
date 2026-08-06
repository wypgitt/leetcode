#
# @lc app=leetcode id=1109 lang=python3
#
# [1109] Corporate Flight Bookings
#
# https://leetcode.com/problems/corporate-flight-bookings/description/
#
# algorithms
# Medium (68.35%)
# Likes:    1916
# Dislikes: 169
# Total Accepted:    118K
# Total Submissions: 173K
# Testcase Example:  "[[1,2,10],[2,3,20],[2,5,25]]"
#
# There are n flights that are labeled from 1 to n.
#
# You are given an array of flight bookings bookings, where bookings[i] =
# [first_i, last_i, seats_i] represents a booking for flights first_i through
# last_i (inclusive) with seats_i seats reserved for each flight in the range.
#
# Return an array answer of length n, where answer[i] is the total number of
# seats reserved for flight i.
#
# Example 1:
#
# Input: bookings = [[1,2,10],[2,3,20],[2,5,25]], n = 5
# Output: [10,55,45,25,25]
# Explanation:
# Flight labels: 1 2 3 4 5
# Booking 1 reserved: 10 10
# Booking 2 reserved: 20 20
# Booking 3 reserved: 25 25 25 25
# Total seats: 10 55 45 25 25
# Hence, answer = [10,55,45,25,25]
#
# Example 2:
#
# Input: bookings = [[1,2,10],[2,2,15]], n = 2
# Output: [10,25]
# Explanation:
# Flight labels: 1 2
# Booking 1 reserved: 10 10
# Booking 2 reserved: 15
# Total seats: 10 25
# Hence, answer = [10,25]
#
# Constraints:
#
# 1 <= n <= 2 * 10^4
#
# 1 <= bookings.length <= 2 * 10^4
#
# bookings[i].length == 3
#
# 1 <= first_i <= last_i <= n
#
# 1 <= seats_i <= 10^4
#

# @lc code=start
from typing import List


class Solution:
    def corpFlightBookings(self, bookings: List[List[int]], n: int) -> List[int]:
        """
        Interview explanation:
        Range updates of +seats on [first,last]: classic difference array.
        Apply +seats at first-1 and -seats at last; prefix sum for answer.

        Algorithm (diff array):
        - diff = [0]*(n+1)
        - For each booking: diff[first-1]+=seats; if last<n: diff[last]-=seats
        - Prefix sum → answer[i].

        Complexity: O(n + m) time, O(n) space.
        """
        diff = [0] * (n + 1)
        for first, last, seats in bookings:
            diff[first - 1] += seats
            diff[last] -= seats
        ans = [0] * n
        cur = 0
        for i in range(n):
            cur += diff[i]
            ans[i] = cur
        return ans
# @lc code=end
