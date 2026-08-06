#
# @lc app=leetcode id=2466 lang=python3
#
# [2466] Count Ways To Build Good Strings
#
# https://leetcode.com/problems/count-ways-to-build-good-strings/description/
#
# algorithms
# Medium (58.84%)
# Likes:    2238
# Dislikes: 210
# Total Accepted:    184.2K
# Total Submissions: 313.1K
# Testcase Example:  "3\n3\n1\n1"
#
# Given the integers zero, one, low, and high, we can construct a string by
# starting with an empty string, and then at each step perform either of the
# following:
#
#
# Append the character '0' zero times.
#
#
# Append the character '1' one times.
#
# This can be performed any number of times.
#
# A good string is a string constructed by the above process having a length
# between low and high (inclusive).
#
# Return the number of different good strings that can be constructed satisfying
# these properties. Since the answer can be large, return it modulo 10^9 + 7.
#
#
#
# Example 1:
#
# Input: low = 3, high = 3, zero = 1, one = 1
# Output: 8
# Explanation:
# One possible valid good string is "011".
# It can be constructed as follows: "" -> "0" -> "01" -> "011".
# All binary strings from "000" to "111" are good strings in this example.
#
# Example 2:
#
# Input: low = 2, high = 3, zero = 1, one = 2
# Output: 5
# Explanation: The good strings are "00", "11", "000", "110", and "011".
#
#
#
# Constraints:
#
#
# 1 <= low <= high <= 10^5
#
#
# 1 <= zero, one <= low
#

# @lc code=start
class Solution:
    def countGoodStrings(self, low: int, high: int, zero: int, one: int) -> int:
        """
        Interview explanation:
        Count strings of length in [low, high] built only by appending '0'*zero
        or '1'*one blocks.

        Algorithm:
        - DP: dp[i] ways to form length i; dp[i]+=dp[i-zero]/dp[i-one].

        Complexity: O(high) time, O(high) space.
        """
        MOD = 10**9 + 7
        dp = [0] * (high + 1)
        dp[0] = 1
        for i in range(1, high + 1):
            if i >= zero:
                dp[i] = (dp[i] + dp[i - zero]) % MOD
            if i >= one:
                dp[i] = (dp[i] + dp[i - one]) % MOD
        return sum(dp[low : high + 1]) % MOD
# @lc code=end

