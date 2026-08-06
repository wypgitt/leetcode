#
# @lc app=leetcode id=1922 lang=python3
#
# [1922] Count Good Numbers
#
# https://leetcode.com/problems/count-good-numbers/description/
#
# algorithms
# Medium (57.95%)
# Likes:    2553
# Dislikes: 604
# Total Accepted:    308K
# Total Submissions: 531K
# Testcase Example:  "1"
#
# A digit string is good if the digits (0-indexed) at even indices are even and
# the digits at odd indices are prime (2, 3, 5, or 7).
#
# For example, "2582" is good because the digits (2 and 8) at even positions
# are even and the digits (5 and 2) at odd positions are prime. However, "3245"
# is not good because 3 is at an even index but is not even.
#
# Given an integer n, return the total number of good digit strings of length
# n. Since the answer may be large, return it modulo 10^9 + 7.
#
# A digit string is a string consisting of digits 0 through 9 that may contain
# leading zeros.
#
# Example 1:
#
# Input: n = 1
# Output: 5
# Explanation: The good numbers of length 1 are "0", "2", "4", "6", "8".
#
# Example 2:
#
# Input: n = 4
# Output: 400
#
# Example 3:
#
# Input: n = 50
# Output: 564908303
#
# Constraints:
#
# 1 <= n <= 10^15
#

# @lc code=start
class Solution:
    def countGoodNumbers(self, n: int) -> int:
        """
        Interview explanation:
        Good digit string: even indices (0-based) use even digit (5 choices),
        odd indices use prime digit (4 choices). Count mod 1e9+7.

        Algorithm:
        - even_positions = (n+1)//2; odd = n//2; pow(5,even)*pow(4,odd) % MOD.

        Complexity: O(log n) time, O(1) space.
        """
        MOD = 10**9 + 7
        return pow(5, (n + 1) // 2, MOD) * pow(4, n // 2, MOD) % MOD
# @lc code=end
