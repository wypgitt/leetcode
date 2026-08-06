#
# @lc app=leetcode id=1736 lang=python3
#
# [1736] Latest Time by Replacing Hidden Digits
#
# https://leetcode.com/problems/latest-time-by-replacing-hidden-digits/description/
#
# algorithms
# Easy (43.96%)
# Likes:    411
# Dislikes: 188
# Total Accepted:    50.0K
# Total Submissions: 114K
# Testcase Example:  "\"2?:?0\""
#
# You are given a string time in the form of hh:mm, where some of the digits in
# the string are hidden (represented by ?).
#
# The valid times are those inclusively between 00:00 and 23:59.
#
# Return the latest valid time you can get from time by replacing the hidden
# digits.
#
# Example 1:
#
# Input: time = "2?:?0"
# Output: "23:50"
# Explanation: The latest hour beginning with the digit '2' is 23 and the
# latest minute ending with the digit '0' is 50.
#
# Example 2:
#
# Input: time = "0?:3?"
# Output: "09:39"
#
# Example 3:
#
# Input: time = "1?:22"
# Output: "19:22"
#
# Constraints:
#
# time is in the format hh:mm.
#
# It is guaranteed that you can produce a valid time from the given string.
#

# @lc code=start
class Solution:
    def maximumTime(self, time: str) -> str:
        """
        Interview explanation:
        Replace "?" in HH:MM to maximize a valid 24-hour time.

        Algorithm:
        - Hour tens: 2 if units allow (<=3), else 1; hour units: 3 if tens==2 else 9.
        - Minute tens max 5; units max 9.

        Complexity: O(1) time, O(1) space.
        """
        h = list(time[:2])
        m = list(time[3:])
        if h[0] == "?":
            h[0] = "2" if h[1] == "?" or h[1] <= "3" else "1"
        if h[1] == "?":
            h[1] = "3" if h[0] == "2" else "9"
        if m[0] == "?":
            m[0] = "5"
        if m[1] == "?":
            m[1] = "9"
        return "".join(h) + ":" + "".join(m)
# @lc code=end
