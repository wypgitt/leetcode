#
# @lc app=leetcode id=552 lang=python3
#
# [552] Student Attendance Record II
#
# https://leetcode.com/problems/student-attendance-record-ii/description/
#
# algorithms
# Hard (56.82%)
# Likes:    2385
# Dislikes: 291
# Total Accepted:    163K
# Total Submissions: 286K
# Testcase Example:  "2"
#
# An attendance record for a student can be represented as a string where each
# character signifies whether the student was absent, late, or present on that
# day. The record only contains the following three characters:
#
# 'A': Absent.
#
# 'L': Late.
#
# 'P': Present.
#
# Any student is eligible for an attendance award if they meet both of the
# following criteria:
#
# The student was absent ('A') for strictly fewer than 2 days total.
#
# The student was never late ('L') for 3 or more consecutive days.
#
# Given an integer n, return the number of possible attendance records of
# length n that make a student eligible for an attendance award. The answer may
# be very large, so return it modulo 10^9 + 7.
#
# Example 1:
#
# Input: n = 2
# Output: 8
# Explanation: There are 8 records with length 2 that are eligible for an
# award:
# "PP", "AP", "PA", "LP", "PL", "AL", "LA", "LL"
# Only "AA" is not eligible because there are 2 absences (there need to be
# fewer than 2).
#
# Example 2:
#
# Input: n = 1
# Output: 3
#
# Example 3:
#
# Input: n = 10101
# Output: 183236316
#
# Constraints:
#
# 1 <= n <= 10^5
#

# @lc code=start
class Solution:
    def checkRecord(self, n: int) -> int:
        """
        Interview explanation:
        DP on (day, absences used, trailing lates): count valid length-n
        records with < 2 total 'A' and no 3 consecutive 'L'. Transitions add
        P / A / L with constraint checks. Mod 10^9+7.

        Algorithm:
        - dp[a][l] = ways with a absences and l trailing Lates.
        - Iterate n days updating from previous state.

        Complexity: O(n) time, O(1) space (6 states).
        """
        MOD = 10**9 + 7
        # dp[absences][trailing_lates]
        dp = [[0] * 3 for _ in range(2)]
        dp[0][0] = 1
        for _ in range(n):
            ndp = [[0] * 3 for _ in range(2)]
            for a in range(2):
                for l in range(3):
                    if dp[a][l] == 0:
                        continue
                    # add P
                    ndp[a][0] = (ndp[a][0] + dp[a][l]) % MOD
                    # add A
                    if a + 1 < 2:
                        ndp[a + 1][0] = (ndp[a + 1][0] + dp[a][l]) % MOD
                    # add L
                    if l + 1 < 3:
                        ndp[a][l + 1] = (ndp[a][l + 1] + dp[a][l]) % MOD
            dp = ndp
        return sum(dp[a][l] for a in range(2) for l in range(3)) % MOD
# @lc code=end

