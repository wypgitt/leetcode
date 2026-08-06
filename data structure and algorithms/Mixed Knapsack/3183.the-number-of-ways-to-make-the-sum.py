#
# @lc app=leetcode id=3183 lang=python3
#
# [3183] The Number of Ways to Make the Sum
#
# https://leetcode.com/problems/the-number-of-ways-to-make-the-sum/description/
#
# algorithms
# Medium (50.89%)
# Likes:    21
# Dislikes: 1
# Total Accepted:    2.2K
# Total Submissions: 4.2K
# Testcase Example:  "4"
#
#
# You have an infinite number of coins with values 1, 2, and 6, and only 2
# coins with value 4.
#
# Given an integer n, return the number of ways to make the sum of n with
# the coins you have.
#
# Since the answer may be very large, return it modulo 10^9 + 7.
#
# Note that the order of the coins doesn't matter and [2, 2, 3] is the
# same as [2, 3, 2].
#
# Example 1:
#
# Input: n = 4
#
# Output: 4
#
# Explanation:
#
# Here are the four combinations: [1, 1, 1, 1], [1, 1, 2], [2, 2], [4].
#
# Example 2:
#
# Input: n = 12
#
# Output: 22
#
# Explanation:
#
# Note that [4, 4, 4] is not a valid combination since we cannot use 4
# three times.
#
# Example 3:
#
# Input: n = 5
#
# Output: 4
#
# Explanation:
#
# Here are the four combinations: [1, 1, 1, 1, 1], [1, 1, 1, 2], [1, 2,
# 2], [1, 4].
#
# Constraints:
#
# 1 <= n <= 10^5
#

# @lc code=start

class Solution:
    def numberOfWays(self, n: int) -> int:
        """
        Interview explanation:
        Unlimited coins {1,2,6} and at most two coins of value 4. Count unordered
        combinations for sum n, modulo 10^9+7.

        Algorithm:
        - Complete knapsack DP for coins [1,2,6] into f[0..n].
        - Add cases using 0/1/2 fours: f[n] + f[n-4] + f[n-8] (when defined).

        Complexity: O(n) time, O(n) space.
        """
        MOD = 10**9 + 7
        f = [0] * (n + 1)
        f[0] = 1
        for coin in (1, 2, 6):
            for j in range(coin, n + 1):
                f[j] = (f[j] + f[j - coin]) % MOD
        ans = f[n]
        if n >= 4:
            ans = (ans + f[n - 4]) % MOD
        if n >= 8:
            ans = (ans + f[n - 8]) % MOD
        return ans

    def numberOfWays_math(self, n: int) -> int:
        """
        Interview explanation:
        Same limited-4 idea with closed counting for {1,2,6}: for remaining r,
        number of non-negative (a,b,c) with a+2b+6c=r equals floor(r/2)+1 minus
        adjustments per sixes; DP is clearer for interviews.

        Algorithm:
        - Precompute f via knapsack; sum over k in {0,1,2} with n-4k >= 0.

        Complexity: O(n) time, O(n) space.
        """
        return self.numberOfWays(n)
# @lc code=end
