#
# @lc app=leetcode id=2777 lang=python3
#
# [2777] Date Range Generator
#
# https://leetcode.com/problems/date-range-generator/description/
#
# algorithms
# Medium (83.06%)
# Likes:    11
# Dislikes: 2
# Total Accepted:    755
# Total Submissions: 909
# Testcase Example:  "\"2023-04-01\"\n\"2023-04-04\"\n1"
#
#
# Given a start date start, an end date end, and a positive integer step,
# return a generator object that yields dates in the range from start to
# end inclusive.
#
# The value of step indicates the number of days between consecutive
# yielded values.
#
# All yielded dates must be in the string format YYYY-MM-DD.
#
# Example 1:
#
# Input: start = "2023-04-01", end = "2023-04-04", step = 1
# Output: ["2023-04-01","2023-04-02","2023-04-03","2023-04-04"]
# Explanation:
# const g = dateRangeGenerator(start, end, step);
# g.next().value // '2023-04-01'
# g.next().value // '2023-04-02'
# g.next().value // '2023-04-03'
# g.next().value // '2023-04-04'
#
# Example 2:
#
# Input: start = "2023-04-10", end = "2023-04-20", step = 3
# Output: ["2023-04-10","2023-04-13","2023-04-16","2023-04-19"]
# Explanation:
# const g = dateRangeGenerator(start, end, step);
# g.next().value // '2023-04-10'
# g.next().value // '2023-04-13'
# g.next().value // '2023-04-16'
# g.next().value // '2023-04-19'
#
# Example 3:
#
# Input: start = "2023-04-10", end = "2023-04-10", step = 1
# Output: ["2023-04-10"]
# Explanation:
# const g = dateRangeGenerator(start, end, step);
# g.next().value // '2023-04-10'
#
# Constraints:
#
# new Date(start) <= new Date(end)
#
# start and end dates are in the string format YYYY-MM-DD
#
# 0 <= The difference in days between the start date and the end date <=
# 1500
#
# 1 <= step <= 1000
#
# @lc code=start
from datetime import datetime, timedelta
from typing import Generator


class Solution:
    def dateRangeGenerator(
        self, start: str, end: str, step: int
    ) -> Generator[str, None, None]:
        """
        Interview explanation:
        JS premium: yield YYYY-MM-DD dates from start to end inclusive, stepping
        by `step` days.

        Algorithm:
        - Parse dates; while current <= end yield and add step days.

        Complexity: O(number of yielded dates).
        """
        cur = datetime.strptime(start, "%Y-%m-%d")
        end_d = datetime.strptime(end, "%Y-%m-%d")
        while cur <= end_d:
            yield cur.strftime("%Y-%m-%d")
            cur += timedelta(days=step)
# @lc code=end
