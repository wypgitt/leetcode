#
# @lc app=leetcode id=681 lang=python3
#
# [681] Next Closest Time
#
# https://leetcode.com/problems/next-closest-time/description/
#
# algorithms
# Medium (47.03%)
# Likes:    744
# Dislikes: 1078
# Total Accepted:    119.2K
# Total Submissions: 253.4K
# Testcase Example:  "\"19:34\""
#
#
# Given a time represented in the format "HH:MM", form the next closest
# time by reusing the current digits. There is no limit on how many times
# a digit can be reused.
#
# You may assume the given input string is always valid. For example,
# "01:34", "12:09" are all valid. "1:34", "12:9" are all invalid.
#
# Example 1:
#
# Input: time = "19:34"
# Output: "19:39"
# Explanation: The next closest time choosing from digits 1, 9, 3, 4, is
# 19:39, which occurs 5 minutes later.
# It is not 19:33, because this occurs 23 hours and 59 minutes later.
#
# Example 2:
#
# Input: time = "23:59"
# Output: "22:22"
# Explanation: The next closest time choosing from digits 2, 3, 5, 9, is
# 22:22.
# It may be assumed that the returned time is next day's time since it is
# smaller than the input time numerically.
#
# Constraints:
#
# time.length == 5
#
# time is a valid time in the form "HH:MM".
#
# 0 <= HH < 24
#
# 0 <= MM < 60
#
# @lc code=start
class Solution:
    def nextClosestTime(self, time: str) -> str:
        """
        Interview explanation:
        Premium: given "HH:MM", form the next valid time (possibly next day)
        using only the digits already present; closest means smallest forward
        minute delta (wrapping).

        Algorithm:
        - Collect unique digits; generate all valid HH:MM from them.
        - Convert current to minutes; among candidates, pick minimal positive
          modular distance (or same time if only one valid).

        Complexity: O(1) — at most 4^4 candidates.
        """
        digits = sorted(set(time[0] + time[1] + time[3] + time[4]))
        cur = int(time[:2]) * 60 + int(time[3:])
        best = None
        best_delta = 24 * 60
        for h1 in digits:
            for h2 in digits:
                hh = int(h1 + h2)
                if hh > 23:
                    continue
                for m1 in digits:
                    for m2 in digits:
                        mm = int(m1 + m2)
                        if mm > 59:
                            continue
                        t = hh * 60 + mm
                        delta = (t - cur) % (24 * 60)
                        if delta == 0:
                            delta = 24 * 60
                        if delta < best_delta:
                            best_delta = delta
                            best = f"{h1}{h2}:{m1}{m2}"
        return best if best is not None else time
# @lc code=end
