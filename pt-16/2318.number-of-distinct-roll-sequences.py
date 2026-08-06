#
# @lc app=leetcode id=2318 lang=python3
#
# [2318] Number of Distinct Roll Sequences
#
# https://leetcode.com/problems/number-of-distinct-roll-sequences/description/
#
# algorithms
# Hard (58.31%)
# Likes:    460
# Dislikes: 20
# Total Accepted:    14.6K
# Total Submissions: 25.1K
# Testcase Example:  "4"
#
# You are given an integer n. You roll a fair 6-sided dice n times. Determine
# the total number of distinct sequences of rolls possible such that the
# following conditions are satisfied:
#
#
# The greatest common divisor of any adjacent values in the sequence is equal to
# 1.
#
#
# There is at least a gap of 2 rolls between equal valued rolls. More formally,
# if the value of the i^th roll is equal to the value of the j^th roll, then
# abs(i - j) > 2.
#
# Return the total number of distinct sequences possible. Since the answer may
# be very large, return it modulo 10^9 + 7.
#
# Two sequences are considered distinct if at least one element is different.
#
#
#
# Example 1:
#
# Input: n = 4
# Output: 184
# Explanation: Some of the possible sequences are (1, 2, 3, 4), (6, 1, 2, 3),
# (1, 2, 3, 1), etc.
# Some invalid sequences are (1, 2, 1, 3), (1, 2, 3, 6).
# (1, 2, 1, 3) is invalid since the first and third roll have an equal value and
# abs(1 - 3) = 2 (i and j are 1-indexed).
# (1, 2, 3, 6) is invalid since the greatest common divisor of 3 and 6 = 3.
# There are a total of 184 distinct sequences possible, so we return 184.
#
# Example 2:
#
# Input: n = 2
# Output: 22
# Explanation: Some of the possible sequences are (1, 2), (2, 1), (3, 2).
# Some invalid sequences are (3, 6), (2, 4) since the greatest common divisor is
# not equal to 1.
# There are a total of 22 distinct sequences possible, so we return 22.
#
#
#
# Constraints:
#
#
# 1 <= n <= 10^4
#

# @lc code=start
from math import gcd


class Solution:
    def distinctSequences(self, n: int) -> int:
        """
        Interview explanation:
        Count length-n dice sequences where adjacent rolls are coprime and no
        number repeats within any window of 2 previous rolls (i.e. roll i !=
        i-1 and i != i-2).

        Algorithm:
        - DP on (prev1, prev2): dp[i][a][b] ways ending with ... a,b.
        - Transition c in 1..6 with gcd(b,c)==1 and c!=a and c!=b.

        Complexity: O(n * 6^3) time, O(6^2) space.
        """
        MOD = 10**9 + 7
        if n == 1:
            return 6
        # dp[a][b] = ways for sequences ending with a,b (1-indexed faces)
        dp = [[0] * 7 for _ in range(7)]
        for a in range(1, 7):
            for b in range(1, 7):
                if a != b and gcd(a, b) == 1:
                    dp[a][b] = 1
        for _ in range(3, n + 1):
            ndp = [[0] * 7 for _ in range(7)]
            for a in range(1, 7):
                for b in range(1, 7):
                    if dp[a][b] == 0:
                        continue
                    for c in range(1, 7):
                        if c != a and c != b and gcd(b, c) == 1:
                            ndp[b][c] = (ndp[b][c] + dp[a][b]) % MOD
            dp = ndp
        return sum(dp[a][b] for a in range(1, 7) for b in range(1, 7)) % MOD

    def distinctSequences_dp(self, n: int) -> int:
        """
        Interview explanation:
        Classic DP over last two rolls (same as primary).

        Algorithm:
        - Iterate length; enforce gcd and distinct-from-last-two.

        Complexity: O(n) time, O(1) space.
        """
        return self.distinctSequences(n)
# @lc code=end
