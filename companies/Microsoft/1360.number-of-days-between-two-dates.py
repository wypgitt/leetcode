#
# @lc app=leetcode id=1360 lang=python3
#
# [1360] Number of Days Between Two Dates
#
# https://leetcode.com/problems/number-of-days-between-two-dates/description/
#
# algorithms
# Easy (53.14%)
# Likes:    443
# Dislikes: 1325
# Total Accepted:    77.3K
# Total Submissions: 145K
# Testcase Example:  "\"2019-06-29\""
#
# Write a program to count the number of days between two dates.
#
# The two dates are given as strings, their format is YYYY-MM-DD as shown in
# the examples.
#
# Example 1:
#
# Input: date1 = "2019-06-29", date2 = "2019-06-30"
# Output: 1
#
# Example 2:
#
# Input: date1 = "2020-01-15", date2 = "2019-12-31"
# Output: 15
#
# Constraints:
#
# The given dates are valid dates between the years 1971 and 2100.
#

# @lc code=start

class Solution:
    def daysBetweenDates(self, date1: str, date2: str) -> int:
        """
        Interview explanation:
        Absolute day difference between two YYYY-MM-DD dates. Convert each to
        days since a fixed epoch accounting for leap years.

        Algorithm:
        - to_days(y,m,d): days from year 1971 + month days + d; leap if y%4==0
          (range 1971-2100 so %100/%400 not needed for correctness here)
        - return abs(to_days(date1)-to_days(date2))

        Complexity: O(1) time, O(1) space.
        """
        def is_leap(y: int) -> bool:
            return y % 4 == 0 and (y % 100 != 0 or y % 400 == 0)

        def to_days(s: str) -> int:
            y, m, d = map(int, s.split("-"))
            mdays = [0, 31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]
            days = d
            for yy in range(1971, y):
                days += 366 if is_leap(yy) else 365
            for mm in range(1, m):
                days += mdays[mm]
                if mm == 2 and is_leap(y):
                    days += 1
            return days

        return abs(to_days(date1) - to_days(date2))

    def daysBetweenDates_datetime(self, date1: str, date2: str) -> int:
        """
        Interview explanation:
        Alternate using datetime.date difference.

        Algorithm:
        - Parse both dates; return abs((d1-d2).days)

        Complexity: O(1).
        """
        from datetime import date
        def parse(s: str) -> date:
            y, m, d = map(int, s.split("-"))
            return date(y, m, d)
        return abs((parse(date1) - parse(date2)).days)
# @lc code=end
