#
# @lc app=leetcode id=3114 lang=python3
#
# [3114] Latest Time You Can Obtain After Replacing Characters
#
# https://leetcode.com/problems/latest-time-you-can-obtain-after-replacing-characters/description/
#
# algorithms
# Easy (35.51%)
# Likes:    122
# Dislikes: 52
# Total Accepted:    42.4K
# Total Submissions: 119.4K
# Testcase Example:  "\"1?:?4\""
#
#
# You are given a string s representing a 12-hour format time where some
# of the digits (possibly none) are replaced with a "?".
#
# 12-hour times are formatted as "HH:MM", where HH is between 00 and 11,
# and MM is between 00 and 59. The earliest 12-hour time is 00:00, and the
# latest is 11:59.
#
# You have to replace all the "?" characters in s with digits such that
# the time we obtain by the resulting string is a valid 12-hour format
# time and is the latest possible.
#
# Return the resulting string.
#
# Example 1:
#
# Input: s = "1?:?4"
#
# Output: "11:54"
#
# Explanation: The latest 12-hour format time we can achieve by replacing
# "?" characters is "11:54".
#
# Example 2:
#
# Input: s = "0?:5?"
#
# Output: "09:59"
#
# Explanation: The latest 12-hour format time we can achieve by replacing
# "?" characters is "09:59".
#
# Constraints:
#
# s.length == 5
#
# s[2] is equal to the character ":".
#
# All characters except s[2] are digits or "?" characters.
#
# The input is generated such that there is at least one time between
# "00:00" and "11:59" that you can obtain after replacing the "?"
# characters.
#

# @lc code=start
class Solution:
    def findLatestTime(self, s: str) -> str:
        """
        Interview explanation:
        Fill '?' in "HH:MM" (00:00–11:59) to get the latest valid 12-hour time.

        Algorithm:
        - Hour tens: prefer 1 if units allow ≤1, else 0.
        - Hour units: 1 if tens is 1 else 9; minutes → 5 and 9.

        Complexity: O(1) time, O(1) space.
        """
        t = list(s)
        if t[0] == "?":
            t[0] = "1" if t[1] in "?01" else "0"
        if t[1] == "?":
            t[1] = "1" if t[0] == "1" else "9"
        if t[3] == "?":
            t[3] = "5"
        if t[4] == "?":
            t[4] = "9"
        return "".join(t)
# @lc code=end
