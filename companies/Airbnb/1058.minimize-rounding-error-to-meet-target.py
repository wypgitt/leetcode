#
# @lc app=leetcode id=1058 lang=python3
#
# [1058] Minimize Rounding Error to Meet Target
#
# https://leetcode.com/problems/minimize-rounding-error-to-meet-target/description/
#
# algorithms
# Medium (45.83%)
# Likes:    157
# Dislikes: 149
# Total Accepted:    11.7K
# Total Submissions: 25.5K
# Testcase Example:  "[\"0.700\",\"2.800\",\"4.900\"]\n8"
#
#
# Given an array of prices [p_1,p_2...,p_n] and a target, round each price
# p_i to Round_i(p_i) so that the rounded array
# [Round_1(p_1),Round_2(p_2)...,Round_n(p_n)] sums to the given target.
# Each operation Round_i(p_i) could be either Floor(p_i) or Ceil(p_i).
#
# Return the string "-1" if the rounded array is impossible to sum to
# target. Otherwise, return the smallest rounding error, which is defined
# as Σ |Round_i(p_i) - (p_i)| for i from 1 to n, as a string with three
# places after the decimal.
#
# Example 1:
#
# Input: prices = ["0.700","2.800","4.900"], target = 8
# Output: "1.000"
# Explanation:
# Use Floor, Ceil and Ceil operations to get (0.7 - 0) + (3 - 2.8) + (5 -
# 4.9) = 0.7 + 0.2 + 0.1 = 1.0 .
#
# Example 2:
#
# Input: prices = ["1.500","2.500","3.500"], target = 10
# Output: "-1"
# Explanation: It is impossible to meet the target.
#
# Example 3:
#
# Input: prices = ["1.500","2.500","3.500"], target = 9
# Output: "1.500"
#
# Constraints:
#
# 1 <= prices.length <= 500
#
# Each string prices[i] represents a real number in the range [0.0,
# 1000.0] and has exactly 3 decimal places.
#
# 0 <= target <= 10^6
#
# @lc code=start
from typing import List


class Solution:
    def minimizeError(self, prices: List[str], target: int) -> str:
        """
        Interview explanation:
        Premium. Each price floor or ceil; sum of chosen integers must equal
        target; minimize total absolute rounding error. Let low = sum(floor);
        need exactly (target-low) ceils among numbers with fractional part >0.
        Pick those with smallest (1-frac) cost to ceil (= frac cost difference).

        Algorithm:
        - Parse floats; low=sum floors; hi=sum ceils
        - If target not in [low,hi]: "-1"
        - need = target-low; among non-integers sort by (1-frac)-(frac)=1-2*frac
          i.e. sort by frac ascending (cheapest to round up have larger frac...
          cost of flooring is frac, cost of ceiling is 1-frac; for the `need`
          we ceil, error = sum of floor-errors for rest + ceil-errors for chosen.
          Equivalent: start all floor (error=sum fracs); switching to ceil changes
          error by (1-frac)-frac = 1-2*frac; pick need smallest (1-2*frac) i.e.
          largest frac.

        Complexity: O(n log n) time, O(n) space.
        """
        fracs = []
        low = 0
        error_floor = 0.0
        for p in prices:
            x = float(p)
            f = int(x)  # floor for positive
            frac = x - f
            low += f
            if abs(frac) < 1e-12:
                continue
            fracs.append(frac)
            error_floor += frac
        hi = low + len(fracs)
        if target < low or target > hi:
            return "-1"
        need = target - low
        # start all floor; switch `need` with largest frac to ceil
        fracs.sort(reverse=True)
        err = error_floor
        for i in range(need):
            err += 1 - 2 * fracs[i]
        return f"{err:.3f}"
# @lc code=end
