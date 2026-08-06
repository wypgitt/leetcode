#
# @lc app=leetcode id=1185 lang=python3
#
# [1185] Day of the Week
#
# https://leetcode.com/problems/day-of-the-week/description/
#
# algorithms
# Easy (59.46%)
# Likes:    461
# Dislikes: 2574
# Total Accepted:    94.6K
# Total Submissions: 159K
# Testcase Example:  "31"
#
# Given a date, return the corresponding day of the week for that date.
#
# The input is given as three integers representing the day, month and year
# respectively.
#
# Return the answer as one of the following values {"Sunday", "Monday",
# "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"}.
#
# Note: January 1, 1971 was a Friday.
#
# Example 1:
#
# Input: day = 31, month = 8, year = 2019
# Output: "Saturday"
#
# Example 2:
#
# Input: day = 18, month = 7, year = 1999
# Output: "Sunday"
#
# Example 3:
#
# Input: day = 15, month = 8, year = 1993
# Output: "Sunday"
#
# Constraints:
#
# The given dates are valid dates between the years 1971 and 2100.
#

# @lc code=start

import datetime


class Solution:
    def dayOfTheWeek(self, day: int, month: int, year: int) -> str:
        """
        Interview explanation:
        Map calendar date to weekday name. Use datetime (or Zeller / known
        epoch: Jan 1 1971 was Friday) then index into day names.

        Algorithm (datetime):
        - datetime.date(year, month, day).weekday() → 0=Mon .. 6=Sun.
        - Map to required English names.

        Complexity: O(1) time/space.
        """
        names = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
        return names[datetime.date(year, month, day).weekday()]

    def dayOfTheWeek_manual(self, day: int, month: int, year: int) -> str:
        """
        Interview explanation:
        Alternate: count days from a known epoch (1971-01-01 = Friday) using
        month lengths and leap-year rules; mod 7.

        Algorithm:
        - days = day-1 + prior months + years since 1971; leap if y%4==0 (and
          century rules in range). (epoch + days) % 7 → name.

        Complexity: O(1) time/space (year span bounded).
        """
        names = ["Friday", "Saturday", "Sunday", "Monday", "Tuesday", "Wednesday", "Thursday"]
        mdays = [31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]

        def is_leap(y: int) -> bool:
            return y % 4 == 0 and (y % 100 != 0 or y % 400 == 0)

        total = 0
        for y in range(1971, year):
            total += 366 if is_leap(y) else 365
        for m in range(1, month):
            total += mdays[m - 1]
            if m == 2 and is_leap(year):
                total += 1
        total += day - 1
        return names[total % 7]
# @lc code=end
