#
# @lc app=leetcode id=2437 lang=python3
#
# [2437] Number of Valid Clock Times
#
# https://leetcode.com/problems/number-of-valid-clock-times/description/
#
# algorithms
# Easy (48.23%)
# Likes:    311
# Dislikes: 248
# Total Accepted:    39.5K
# Total Submissions: 81.9K
# Testcase Example:  "\"?5:00\""
#
# You are given a string of length 5 called time, representing the current time
# on a digital clock in the format "hh:mm". The earliest possible time is
# "00:00" and the latest possible time is "23:59".
#
# In the string time, the digits represented by the ? symbol are unknown, and
# must be replaced with a digit from 0 to 9.
#
# Return an integer answer, the number of valid clock times that can be created
# by replacing every ? with a digit from 0 to 9.
#
#
#
# Example 1:
#
# Input: time = "?5:00"
# Output: 2
# Explanation: We can replace the ? with either a 0 or 1, producing "05:00" or
# "15:00". Note that we cannot replace it with a 2, since the time "25:00" is
# invalid. In total, we have two choices.
#
# Example 2:
#
# Input: time = "0?:0?"
# Output: 100
# Explanation: Each ? can be replaced by any digit from 0 to 9, so we have 100
# total choices.
#
# Example 3:
#
# Input: time = "??:??"
# Output: 1440
# Explanation: There are 24 possible choices for the hours, and 60 possible
# choices for the minutes. In total, we have 24 * 60 = 1440 choices.
#
#
#
# Constraints:
#
#
# time is a valid string of length 5 in the format "hh:mm".
#
#
# "00" <= hh <= "23"
#
#
# "00" <= mm <= "59"
#
#
# Some of the digits might be replaced with '?' and need to be replaced with
# digits from 0 to 9.
#

# @lc code=start
class Solution:
    def countTime(self, time: str) -> int:
        """
        Interview explanation:
        "HH:MM" with '?' wildcards; count valid clock times.

        Algorithm:
        - Enumerate hours 0..23 and minutes 0..59 matching the pattern.

        Complexity: O(1) (24*60), O(1) space.
        """
        def match(pat: str, val: str) -> bool:
            return all(p == "?" or p == v for p, v in zip(pat, val))

        ans = 0
        for h in range(24):
            for m in range(60):
                if match(time, f"{h:02d}:{m:02d}"):
                    ans += 1
        return ans

    def countTime_math(self, time: str) -> int:
        """
        Interview explanation:
        Alternate: multiply valid hour choices by valid minute choices.

        Algorithm:
        - Case enumeration per HH and MM independently.

        Complexity: O(1).
        """
        h1, h2, _, m1, m2 = time
        hours = mins = 0
        for h in range(24):
            a, b = divmod(h, 10)
            if (h1 == "?" or int(h1) == a) and (h2 == "?" or int(h2) == b):
                hours += 1
        for m in range(60):
            a, b = divmod(m, 10)
            if (m1 == "?" or int(m1) == a) and (m2 == "?" or int(m2) == b):
                mins += 1
        return hours * mins
# @lc code=end
