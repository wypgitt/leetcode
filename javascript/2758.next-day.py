#
# @lc app=leetcode id=2758 lang=python3
#
# [2758] Next Day
#
# https://leetcode.com/problems/next-day/description/
#
# algorithms
# Easy (84.89%)
# Likes:    14
# Dislikes: 1
# Total Accepted:    1.7K
# Total Submissions: 2K
# Testcase Example:  "\"2014-06-20\""
#
#
# Write code that enhances all date objects such that you can call the
# date.nextDay() method on any date object and it will return the next day
# in the format YYYY-MM-DD as a string.
#
# Example 1:
#
# Input: date = "2014-06-20"
# Output: "2014-06-21"
# Explanation:
# const date = new Date("2014-06-20");
# date.nextDay(); // "2014-06-21"
#
# Example 2:
#
# Input: date = "2017-10-31"
# Output: "2017-11-01"
# Explanation: The day after 2017-10-31 is 2017-11-01.
#
# Constraints:
#
# new Date(date) is a valid date object
#
# @lc code=start
from datetime import datetime, timedelta


class Solution:
    def nextDay(self, date_str: str) -> str:
        """
        Interview explanation:
        JS premium: Date.prototype.nextDay — return next calendar day as YYYY-MM-DD.

        Algorithm:
        - Parse, add one day, format.

        Complexity: O(1).
        """
        d = datetime.strptime(date_str[:10], "%Y-%m-%d") + timedelta(days=1)
        return d.strftime("%Y-%m-%d")
# @lc code=end
