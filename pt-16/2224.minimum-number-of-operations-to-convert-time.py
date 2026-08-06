#
# @lc app=leetcode id=2224 lang=python3
#
# [2224] Minimum Number of Operations to Convert Time
#
# https://leetcode.com/problems/minimum-number-of-operations-to-convert-time/description/
#
# algorithms
# Easy (66.44%)
# Likes:    506
# Dislikes: 39
# Total Accepted:    57.2K
# Total Submissions: 86K
# Testcase Example:  "\"02:30\"\n\"04:35\""
#
# You are given two strings current and correct representing two 24-hour times.
#
# 24-hour times are formatted as "HH:MM", where HH is between 00 and 23, and MM
# is between 00 and 59. The earliest 24-hour time is 00:00, and the latest is
# 23:59.
#
# In one operation you can increase the time current by 1, 5, 15, or 60 minutes.
# You can perform this operation any number of times.
#
# Return the minimum number of operations needed to convert current to correct.
#
#
#
# Example 1:
#
# Input: current = "02:30", correct = "04:35"
# Output: 3
# Explanation:
# We can convert current to correct in 3 operations as follows:
# - Add 60 minutes to current. current becomes "03:30".
# - Add 60 minutes to current. current becomes "04:30".
# - Add 5 minutes to current. current becomes "04:35".
# It can be proven that it is not possible to convert current to correct in
# fewer than 3 operations.
#
# Example 2:
#
# Input: current = "11:00", correct = "11:01"
# Output: 1
# Explanation: We only have to add one minute to current, so the minimum number
# of operations needed is 1.
#
#
#
# Constraints:
#
#
# current and correct are in the format "HH:MM"
#
#
# current <= correct
#

# @lc code=start
class Solution:
    def convertTime(self, current: str, correct: str) -> int:
        """
        Interview explanation:
        Convert current HH:MM to correct by adding 60,15,5, or 1 minutes; min ops.

        Algorithm:
        - Diff minutes; greedy with coins 60,15,5,1 (canonical).

        Complexity: O(1) time, O(1) space.
        """
        def to_min(t: str) -> int:
            h, m = map(int, t.split(":"))
            return h * 60 + m

        diff = to_min(correct) - to_min(current)
        ops = 0
        for step in (60, 15, 5, 1):
            ops += diff // step
            diff %= step
        return ops
# @lc code=end
