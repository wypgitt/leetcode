#
# @lc app=leetcode id=3490 lang=python3
#
# [3490] Count Beautiful Numbers
#
# https://leetcode.com/problems/count-beautiful-numbers/description/
#
# algorithms
# Hard (24.09%)
# Likes:    60
# Dislikes: 3
# Total Accepted:    6K
# Total Submissions: 25K
# Testcase Example:  "10\n20"
#
#
# You are given two positive integers, l and r. A positive integer is
# called beautiful if the product of its digits is divisible by the sum of
# its digits.
#
# Return the count of beautiful numbers between l and r, inclusive.
#
# Example 1:
#
# Input: l = 10, r = 20
#
# Output: 2
#
# Explanation:
#
# The beautiful numbers in the range are 10 and 20.
#
# Example 2:
#
# Input: l = 1, r = 15
#
# Output: 10
#
# Explanation:
#
# The beautiful numbers in the range are 1, 2, 3, 4, 5, 6, 7, 8, 9, and
# 10.
#
# Constraints:
#
# 1 <= l <= r < 10^9
#

# @lc code=start
from functools import lru_cache


class Solution:
    def beautifulNumbers(self, l: int, r: int) -> int:
        """
        Interview explanation:
        Count numbers in [l, r] whose digit-product is divisible by digit-sum.
        Bounds up to 1e9 → digit DP.

        Algorithm:
        - Digit DP over upper bound: state (pos, tight, leading_zero, sum, prod).
        - If a non-leading zero appears, product is 0 → always beautiful.
        - Answer = count(r) - count(l - 1).

        Complexity: O(digits * sum * prod_states * 10) with memo; digits ≤ 10,
        sum ≤ 90; product pruned by zero / leading-zero cases.
        """

        def count_upto(n: int) -> int:
            if n < 0:
                return 0
            digits = list(map(int, str(n)))

            @lru_cache(None)
            def dp(i: int, tight: bool, leading: bool, sm: int, prod: int) -> int:
                if i == len(digits):
                    if leading:
                        return 0
                    return 1 if sm > 0 and prod % sm == 0 else 0

                limit = digits[i] if tight else 9
                res = 0
                for d in range(limit + 1):
                    nt = tight and d == limit
                    if leading and d == 0:
                        res += dp(i + 1, nt, True, 0, 1)
                    else:
                        res += dp(i + 1, nt, False, sm + d, prod * d)
                return res

            return dp(0, True, True, 0, 1)

        return count_upto(r) - count_upto(l - 1)
# @lc code=end
