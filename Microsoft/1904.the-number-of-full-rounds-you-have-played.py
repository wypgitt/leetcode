#
# @lc app=leetcode id=1904 lang=python3
#
# [1904] The Number of Full Rounds You Have Played
#
# https://leetcode.com/problems/the-number-of-full-rounds-you-have-played/description/
#
# algorithms
# Medium (43.44%)
# Likes:    233
# Dislikes: 265
# Total Accepted:    26.4K
# Total Submissions: 60.7K
# Testcase Example:  "\"09:31\""
#
# You are participating in an online chess tournament. There is a chess round
# that starts every 15 minutes. The first round of the day starts at 00:00, and
# after every 15 minutes, a new round starts.
#
# For example, the second round starts at 00:15, the fourth round starts at
# 00:45, and the seventh round starts at 01:30.
#
# You are given two strings loginTime and logoutTime where:
#
# loginTime is the time you will login to the game, and
#
# logoutTime is the time you will logout from the game.
#
# If logoutTime is earlier than loginTime, this means you have played from
# loginTime to midnight and from midnight to logoutTime.
#
# Return the number of full chess rounds you have played in the tournament.
#
# Note: All the given times follow the 24-hour clock. That means the first
# round of the day starts at 00:00 and the last round of the day starts at
# 23:45.
#
# Example 1:
#
# Input: loginTime = "09:31", logoutTime = "10:14"
# Output: 1
# Explanation: You played one full round from 09:45 to 10:00.
# You did not play the full round from 09:30 to 09:45 because you logged in at
# 09:31 after it began.
# You did not play the full round from 10:00 to 10:15 because you logged out at
# 10:14 before it ended.
#
# Example 2:
#
# Input: loginTime = "21:30", logoutTime = "03:00"
# Output: 22
# Explanation: You played 10 full rounds from 21:30 to 00:00 and 12 full rounds
# from 00:00 to 03:00.
# 10 + 12 = 22.
#
# Constraints:
#
# loginTime and logoutTime are in the format hh:mm.
#
# 00 <= hh <= 23
#
# 00 <= mm <= 59
#
# loginTime and logoutTime are not equal.
#

# @lc code=start
class Solution:
    def numberOfRounds(self, loginTime: str, logoutTime: str) -> int:
        """
        Interview explanation:
        Full 15-minute rounds [HH:00,HH:15,...] fully contained in [login,logout).
        If logout <= login, session wraps past midnight (+24h).

        Algorithm:
        - Convert to minutes. start = ceil(login/15)*15; end = floor(logout/15)*15.
          Return max(0, (end-start)//15).

        Complexity: O(1) time/space.
        """
        def to_min(t: str) -> int:
            h, m = map(int, t.split(":"))
            return h * 60 + m

        a, b = to_min(loginTime), to_min(logoutTime)
        if b <= a:
            b += 24 * 60
        start = (a + 14) // 15 * 15
        end = b // 15 * 15
        return max(0, (end - start) // 15)
# @lc code=end
