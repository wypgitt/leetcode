#
# @lc app=leetcode id=2409 lang=python3
#
# [2409] Count Days Spent Together
#
# https://leetcode.com/problems/count-days-spent-together/description/
#
# algorithms
# Easy (48.31%)
# Likes:    289
# Dislikes: 593
# Total Accepted:    32K
# Total Submissions: 66.3K
# Testcase Example:  "\"08-15\"\n\"08-18\"\n\"08-16\"\n\"08-19\""
#
# Alice and Bob are traveling to Rome for separate business meetings.
#
# You are given 4 strings arriveAlice, leaveAlice, arriveBob, and leaveBob.
# Alice will be in the city from the dates arriveAlice to leaveAlice
# (inclusive), while Bob will be in the city from the dates arriveBob to
# leaveBob (inclusive). Each will be a 5-character string in the format "MM-DD",
# corresponding to the month and day of the date.
#
# Return the total number of days that Alice and Bob are in Rome together.
#
# You can assume that all dates occur in the same calendar year, which is not a
# leap year. Note that the number of days per month can be represented as: [31,
# 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31].
#
#
#
# Example 1:
#
# Input: arriveAlice = "08-15", leaveAlice = "08-18", arriveBob = "08-16",
# leaveBob = "08-19"
# Output: 3
# Explanation: Alice will be in Rome from August 15 to August 18. Bob will be in
# Rome from August 16 to August 19. They are both in Rome together on August
# 16th, 17th, and 18th, so the answer is 3.
#
# Example 2:
#
# Input: arriveAlice = "10-01", leaveAlice = "10-31", arriveBob = "11-01",
# leaveBob = "12-31"
# Output: 0
# Explanation: There is no day when Alice and Bob are in Rome together, so we
# return 0.
#
#
#
# Constraints:
#
#
# All dates are provided in the format "MM-DD".
#
#
# Alice and Bob's arrival dates are earlier than or equal to their leaving
# dates.
#
#
# The given dates are valid dates of a non-leap year.
#

# @lc code=start
class Solution:
    def countDaysTogether(
        self, arriveAlice: str, leaveAlice: str, arriveBob: str, leaveBob: str
    ) -> int:
        """
        Interview explanation:
        Count overlapping inclusive days Alice and Bob are both present (same year,
        non-leap). Dates given as "MM-DD".

        Algorithm:
        - Convert to day-of-year; intersection length of [a1,a2] and [b1,b2].

        Complexity: O(1) time/space.
        """
        mdays = [0, 31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]
        pref = [0]
        for d in mdays[1:]:
            pref.append(pref[-1] + d)

        def to_day(s: str) -> int:
            m, d = int(s[:2]), int(s[3:])
            return pref[m - 1] + d

        a1, a2 = to_day(arriveAlice), to_day(leaveAlice)
        b1, b2 = to_day(arriveBob), to_day(leaveBob)
        start, end = max(a1, b1), min(a2, b2)
        return max(0, end - start + 1)
# @lc code=end
