#
# @lc app=leetcode id=1507 lang=python3
#
# [1507] Reformat Date
#
# https://leetcode.com/problems/reformat-date/description/
#
# algorithms
# Easy (68.78%)
# Likes:    507
# Dislikes: 441
# Total Accepted:    101K
# Total Submissions: 146K
# Testcase Example:  "\"20th Oct 2052\""
#
# Given a date string in the form Day Month Year, where:
#
# Day is in the set {"1st", "2nd", "3rd", "4th", ..., "30th", "31st"}.
#
# Month is in the set {"Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug",
# "Sep", "Oct", "Nov", "Dec"}.
#
# Year is in the range [1900, 2100].
#
# Convert the date string to the format YYYY-MM-DD, where:
#
# YYYY denotes the 4 digit year.
#
# MM denotes the 2 digit month.
#
# DD denotes the 2 digit day.
#
# Example 1:
#
# Input: date = "20th Oct 2052"
# Output: "2052-10-20"
#
# Example 2:
#
# Input: date = "6th Jun 1933"
# Output: "1933-06-06"
#
# Example 3:
#
# Input: date = "26th May 1960"
# Output: "1960-05-26"
#
# Constraints:
#
# The given dates are guaranteed to be valid, so no error handling is
# necessary.
#

# @lc code=start
class Solution:
    def reformatDate(self, date: str) -> str:
        """
        Interview explanation:
        Input like "20th Oct 2052" → "2052-10-20". Parse day/month/year;
        map month abbreviation to number; zero-pad day/month.

        Algorithm:
        - Split; strip ordinal from day; month dict; format YYYY-MM-DD.

        Complexity: O(1) time/space.
        """
        months = {
            "Jan": "01", "Feb": "02", "Mar": "03", "Apr": "04",
            "May": "05", "Jun": "06", "Jul": "07", "Aug": "08",
            "Sep": "09", "Oct": "10", "Nov": "11", "Dec": "12",
        }
        d, m, y = date.split()
        day = d[:-2].zfill(2)
        return f"{y}-{months[m]}-{day}"
# @lc code=end
