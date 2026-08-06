#
# @lc app=leetcode id=3986 lang=python3
#
# [3986] Number of Elapsed Seconds Between Two Times
#
# https://leetcode.com/problems/number-of-elapsed-seconds-between-two-times/description/
#
# algorithms
# Easy (82.17%)
# Likes:    41
# Dislikes: 3
# Total Accepted:    50.3K
# Total Submissions: 61.3K
# Testcase Example:  "\"01:00:00\"\n\"01:00:25\""
#
#
# You are given two valid times startTime and endTime, each represented as
# a string in the format "HH:MM:SS".
#
# Return the number of seconds that have elapsed from startTime to
# endTime.
#
# Example 1:
#
# Input: startTime = "01:00:00", endTime = "01:00:25"
#
# Output: 25
#
# Explanation:
#
# endTime is 25 seconds ahead of startTime.
#
# Example 2:
#
# Input: startTime = "12:34:56", endTime = "13:00:00"
#
# Output: 1504
#
# Explanation:
#
# endTime is 25 minutes and 4 seconds ahead of startTime, which equals
# 1504 seconds.
#
# Constraints:
#
# startTime.length == 8
#
# endTime.length == 8
#
# startTime and endTime are valid times in the format "HH:MM:SS"
#
# 00 <= HH <= 23
#
# 00 <= MM <= 59
#
# 00 <= SS <= 59
#
# endTime is not earlier than startTime
#

# @lc code=start
class Solution:
    def secondsBetweenTimes(self, startTime: str, endTime: str) -> int:
        """
        Interview explanation:
        Convert each HH:MM:SS to seconds since midnight and subtract.
        endTime is never earlier than startTime.

        Algorithm:
        - f(s) = HH*3600 + MM*60 + SS; return f(end) - f(start).

        Complexity: O(1) time and space.
        """
        def to_sec(s: str) -> int:
            return int(s[:2]) * 3600 + int(s[3:5]) * 60 + int(s[6:])

        return to_sec(endTime) - to_sec(startTime)
# @lc code=end
