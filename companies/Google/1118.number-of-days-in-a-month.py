#
# @lc app=leetcode id=1118 lang=python3
#
# [1118] Number of Days in a Month
#
# https://leetcode.com/problems/number-of-days-in-a-month/description/
#
# algorithms
# Easy (59.41%)
# Likes:    47
# Dislikes: 180
# Total Accepted:    9.8K
# Total Submissions: 16.6K
# Testcase Example:  "1992\n7"
#
#
# Given a year year and a month month, return the number of days of that
# month.
#
# Example 1:
#
# Input: year = 1992, month = 7
# Output: 31
#
# Example 2:
#
# Input: year = 2000, month = 2
# Output: 29
#
# Example 3:
#
# Input: year = 1900, month = 2
# Output: 28
#
# Constraints:
#
# 1583 <= year <= 2100
#
# 1 <= month <= 12
#
# @lc code=start
class Solution:
    def numberOfDays(self, year: int, month: int) -> int:
        """
        Interview explanation:
        Premium. Return days in (year, month), handling leap years for February
        (div by 4, not century unless div by 400).

        Algorithm:
        - days = [0,31,28,31,30,31,30,31,31,30,31,30,31]
        - If month==2 and leap(year): return 29 else days[month].

        Complexity: O(1).
        """
        days = [0, 31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]
        if month == 2 and ((year % 4 == 0 and year % 100 != 0) or year % 400 == 0):
            return 29
        return days[month]
# @lc code=end
