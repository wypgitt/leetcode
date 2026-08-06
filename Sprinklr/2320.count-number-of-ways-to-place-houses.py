#
# @lc app=leetcode id=2320 lang=python3
#
# [2320] Count Number of Ways to Place Houses
#
# https://leetcode.com/problems/count-number-of-ways-to-place-houses/description/
#
# algorithms
# Medium (44.11%)
# Likes:    647
# Dislikes: 204
# Total Accepted:    38.1K
# Total Submissions: 86.3K
# Testcase Example:  "1"
#
# There is a street with n * 2 plots, where there are n plots on each side of
# the street. The plots on each side are numbered from 1 to n. On each plot, a
# house can be placed.
#
# Return the number of ways houses can be placed such that no two houses are
# adjacent to each other on the same side of the street. Since the answer may be
# very large, return it modulo 10^9 + 7.
#
# Note that if a house is placed on the i^th plot on one side of the street, a
# house can also be placed on the i^th plot on the other side of the street.
#
#
#
# Example 1:
#
# Input: n = 1
# Output: 4
# Explanation:
# Possible arrangements:
# 1. All plots are empty.
# 2. A house is placed on one side of the street.
# 3. A house is placed on the other side of the street.
# 4. Two houses are placed, one on each side of the street.
#
# Example 2:
#
# Input: n = 2
# Output: 9
# Explanation: The 9 possible arrangements are shown in the diagram above.
#
#
#
# Constraints:
#
#
# 1 <= n <= 10^4
#

# @lc code=start
class Solution:
    def countHousePlacements(self, n: int) -> int:
        """
        Interview explanation:
        Street of n plots on each side; place houses so no two adjacent on the
        same side. Sides independent. Return ways mod 1e9+7.

        Algorithm:
        - One side is Fibonacci: a_i = empty/occupied endings; ways_one = F_{n+2}.
        - Total = ways_one^2.

        Complexity: O(n) time, O(1) space.
        """
        MOD = 10**9 + 7
        # fib: number of binary strings of length n with no two consecutive 1s
        a, b = 1, 1  # len 0 empty=1; after 1 plot: empty or house -> 2 = a+b style
        # Let e=ways ending empty, h=ending house for length i
        e, h = 1, 1  # length 1
        for _ in range(2, n + 1):
            e, h = (e + h) % MOD, e
        one = (e + h) % MOD
        return (one * one) % MOD

    def countHousePlacements_dp(self, n: int) -> int:
        """
        Interview explanation:
        Fibonacci DP for one side, square it (same as primary).

        Algorithm:
        - dp[i] = dp[i-1]+dp[i-2] style placements; square mod MOD.

        Complexity: O(n) time, O(1) space.
        """
        return self.countHousePlacements(n)
# @lc code=end
