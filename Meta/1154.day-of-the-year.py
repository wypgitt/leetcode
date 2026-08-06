#
# @lc app=leetcode id=1154 lang=python3
#
# [1154] Day of the Year
#
# https://leetcode.com/problems/day-of-the-year/description/
#
# algorithms
# Easy (50.09%)
# Likes:    518
# Dislikes: 496
# Total Accepted:    102K
# Total Submissions: 203K
# Testcase Example:  "\"2019-01-09\""
#
# Given a string date representing a Gregorian calendar date formatted as
# YYYY-MM-DD, return the day number of the year.
#
# Example 1:
#
# Input: date = "2019-01-09"
# Output: 9
# Explanation: Given date is the 9th day of the year in 2019.
#
# Example 2:
#
# Input: date = "2019-02-10"
# Output: 41
#
# Constraints:
#
# date.length == 10
#
# date[4] == date[7] == '-', and all other date[i]'s are digits
#
# date represents a calendar date between Jan 1^st, 1900 and Dec 31^st, 2019.
#

# @lc code=start
class Solution:
    def dayOfYear(self, date: str) -> int:
        """
        Interview explanation:
        Given YYYY-MM-DD, return day-of-year. Account for leap years (Feb 29).

        Algorithm:
        - Parse y,m,d; prefix month lengths; +1 to Feb if leap and m>2.

        Complexity: O(1) time/space.
        """
        y, m, d = map(int, date.split("-"))
        days = [31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]
        leap = y % 4 == 0 and (y % 100 != 0 or y % 400 == 0)
        if leap:
            days[1] = 29
        return sum(days[: m - 1]) + d
# @lc code=end
