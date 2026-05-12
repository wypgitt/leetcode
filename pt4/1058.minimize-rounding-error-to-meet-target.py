#
# @lc app=leetcode id=1058 lang=python3
#
# [1058] Minimize Rounding Error to Meet Target
#
# https://leetcode.com/problems/minimize-rounding-error-to-meet-target/description/
#
# algorithms
# Medium (45.87%)
# Likes:    157
# Dislikes: 149
# Total Accepted:    11.5K
# Total Submissions: 25.1K
# Testcase Example:  '["0.700","2.800","4.900"]\n8'
#
# Given an array of prices [p1,p2...,pn] and a target, round each price pi to
# Roundi(pi) so that the rounded array [Round1(p1),Round2(p2)...,Roundn(pn)]
# sums to the given target. Each operation Roundi(pi) could be either Floor(pi)
# or Ceil(pi).
# 
# Return the string "-1" if the rounded array is impossible to sum to target.
# Otherwise, return the smallest rounding error, which is defined as Σ
# |Roundi(pi) - (pi)| for i from 1 to n, as a string with three places after
# the decimal.
# 
# 
# Example 1:
# 
# 
# Input: prices = ["0.700","2.800","4.900"], target = 8
# Output: "1.000"
# Explanation:
# Use Floor, Ceil and Ceil operations to get (0.7 - 0) + (3 - 2.8) + (5 - 4.9)
# = 0.7 + 0.2 + 0.1 = 1.0 .
# 
# 
# Example 2:
# 
# 
# Input: prices = ["1.500","2.500","3.500"], target = 10
# Output: "-1"
# Explanation: It is impossible to meet the target.
# 
# 
# Example 3:
# 
# 
# Input: prices = ["1.500","2.500","3.500"], target = 9
# Output: "1.500"
# 
# 
# 
# Constraints:
# 
# 
# 1 <= prices.length <= 500
# Each string prices[i] represents a real number in the range [0.0, 1000.0] and
# has exactly 3 decimal places.
# 0 <= target <= 10^6
# 
# 
#

# @lc code=start
from typing import List


class Solution:
    def minimizeError(self, prices: List[str], target: int) -> str:
        floor_sum = 0
        fractions = []

        for price in prices:
            whole_part, fraction_part = price.split(".")
            whole = int(whole_part)
            fraction = int(fraction_part)

            floor_sum += whole
            if fraction:
                fractions.append(fraction)

        ceilings_needed = target - floor_sum
        if ceilings_needed < 0 or ceilings_needed > len(fractions):
            return "-1"

        fractions.sort(reverse=True)
        error_thousandths = sum(fractions)

        for fraction in fractions[:ceilings_needed]:
            error_thousandths += 1000 - 2 * fraction

        return f"{error_thousandths // 1000}.{error_thousandths % 1000:03d}"
# @lc code=end

"""
Interview Explanation

Core idea:
Every non-integer price must be rounded either down or up. Start by rounding
all prices down. If the floor sum is short of target by k, exactly k non-
integer prices must be rounded up instead.

Algorithm:
1. Parse each price as integer thousandths to avoid floating-point error.
2. Add all floor values to floor_sum.
3. Collect nonzero fractional parts.
4. Let ceilings_needed = target - floor_sum.
5. If ceilings_needed is outside [0, number of non-integer prices], return -1.
6. Rounding a fraction f up changes error from f to 1000 - f, a delta of
   1000 - 2f. Choose the largest fractions to minimize this delta.
7. Format the integer thousandths as exactly three decimal places.

Data structure choice:
A list of fractional thousandths is enough. Sorting descending directly gives
the fractions that benefit most from rounding up.

Correctness:
The number of ceil operations is forced by the target once all floors are
chosen. For any two fractions a > b, rounding up a instead of b has delta
1000 - 2a, which is smaller than 1000 - 2b. Therefore an optimal solution
rounds up the k largest fractional parts. The algorithm does exactly that.

Complexity:
Parsing is O(n), sorting fractions is O(n log n), and space is O(n).

Tests and edge cases:
- Target below floor_sum or above max possible sum returns -1.
- Integer prices have no rounding choice and no error.
- Need zero ceilings: all non-integers are floored.
- Need all ceilings: every non-integer is ceiled.
- Decimal formatting always prints three places, such as "1.000".
"""
