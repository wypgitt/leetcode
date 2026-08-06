#
# @lc app=leetcode id=3855 lang=python3
#
# [3855] Sum of K-Digit Numbers in a Range
#
# https://leetcode.com/problems/sum-of-k-digit-numbers-in-a-range/description/
#
# algorithms
# Hard (50.88%)
# Likes:    50
# Dislikes: 5
# Total Accepted:    7.2K
# Total Submissions: 14.1K
# Testcase Example:  "1\n2\n2"
#
#
# You are given three integers l, r, and k.
#
# Consider all possible integers consisting of exactly k digits, where
# each digit is chosen independently from the integer range [l, r]
# (inclusive). If 0 is included in the range, leading zeros are allowed.
#
# Return an integer representing the sum of all such numbers.​​​​​​​ Since
# the answer may be very large, return it modulo 10^9 + 7.
#
# Example 1:
#
# Input: l = 1, r = 2, k = 2
#
# Output: 66
#
# Explanation:
#
# All numbers formed using k = 2 digits in the range [1, 2] are 11, 12,
# 21, 22.
#
# The total sum is 11 + 12 + 21 + 22 = 66.
#
# Example 2:
#
# Input: l = 0, r = 1, k = 3
#
# Output: 444
#
# Explanation:
#
# All numbers formed using k = 3 digits in the range [0, 1] are 000, 001,
# 010, 011, 100, 101, 110, 111​​​​​​​.
#
# These numbers without leading zeros are 0, 1, 10, 11, 100, 101, 110,
# 111.
#
# The total sum is 444.
#
# Example 3:
#
# Input: l = 5, r = 5, k = 10
#
# Output: 555555520
#
# Explanation:​​​​​​​
#
# 5555555555 is the only valid number consisting of k = 10 digits in the
# range [5, 5].
#
# The total sum is 5555555555 % (10^9 + 7) = 555555520.
#
# Constraints:
#
# 0 <= l <= r <= 9
#
# 1 <= k <= 10^9
#

# @lc code=start
class Solution:
    MOD = 1_000_000_007

    def sumOfNumbers(self, l: int, r: int, k: int) -> int:
        """
        Interview explanation:
        Sum all k-digit numbers whose every digit is independently in [l, r]
        (leading zeros allowed), modulo 10^9+7.

        Algorithm:
        - Each position contributes the same digit-sum average across place values.
        - digit_sum = sum of allowed digits; other_positions = count^(k-1).
        - Multiply by repunit 111...1 (k ones) for place-value weights.

        Complexity: O(log k) time (modular pow), O(1) space.
        """
        mod = self.MOD
        count = r - l + 1
        digit_sum = (l + r) * count // 2

        other_positions = pow(count, k - 1, mod)
        repunit = (pow(10, k, mod) - 1) * pow(9, mod - 2, mod) % mod

        return digit_sum % mod * other_positions % mod * repunit % mod
# @lc code=end
