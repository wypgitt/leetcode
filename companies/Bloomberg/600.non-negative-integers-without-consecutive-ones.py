#
# @lc app=leetcode id=600 lang=python3
#
# [600] Non-negative Integers without Consecutive Ones
#
# https://leetcode.com/problems/non-negative-integers-without-consecutive-ones/description/
#
# algorithms
# Hard (42.96%)
# Likes:    1660
# Dislikes: 138
# Total Accepted:    55.6K
# Total Submissions: 129K
# Testcase Example:  "5"
#
# Given a positive integer n, return the number of the integers in the range
# [0, n] whose binary representations do not contain consecutive ones.
#
# Example 1:
#
# Input: n = 5
# Output: 5
# Explanation:
# Here are the non-negative integers <= 5 with their corresponding binary
# representations:
# 0 : 0
# 1 : 1
# 2 : 10
# 3 : 11
# 4 : 100
# 5 : 101
# Among them, only integer 3 disobeys the rule (two consecutive ones) and the
# other 5 satisfy the rule.
#
# Example 2:
#
# Input: n = 1
# Output: 2
#
# Example 3:
#
# Input: n = 2
# Output: 3
#
# Constraints:
#
# 1 <= n <= 10^9
#


# @lc code=start
class Solution:
    def findIntegers(self, n: int) -> int:
        """
        Interview explanation:
        Count integers in [0, n] whose binary form has no adjacent 1s. Digit DP
        / Fibonacci structure: the count of valid k-bit strings is Fibonacci;
        walk n's bits from MSB, and whenever we see a 1 we may add all valid
        numbers that place 0 at that bit and freely fill lower bits (with the
        no-consecutive-1s constraint). If two consecutive 1s appear in n, stop
        early (all larger same-prefix numbers are invalid / already counted).

        Algorithm:
        - Precompute f[i] = # valid i-bit strings (incl. leading zeros) =
          f[i-1] + f[i-2] (end with 0 / 01 pattern → Fib).
        - Scan bits of n from high to low; if bit i is 1, add f[i] for choosing
          0 there; if previous bit was also 1, break; else continue.
        - Add 1 at the end to include n itself if valid (or account via the walk).

        Complexity: O(log n) time and space for bit length.
        """
        # f[i] = number of valid bit-strings of length i (leading zeros allowed)
        f = [0] * 32
        f[0], f[1] = 1, 2
        for i in range(2, 32):
            f[i] = f[i - 1] + f[i - 2]

        ans = 0
        prev_bit = 0
        # check bits from 30 down to 0 (n fits in 31 bits for constraints)
        for i in range(30, -1, -1):
            if n & (1 << i):
                ans += f[i]
                if prev_bit == 1:
                    return ans
                prev_bit = 1
            else:
                prev_bit = 0
        return ans + 1  # include n itself
# @lc code=end

