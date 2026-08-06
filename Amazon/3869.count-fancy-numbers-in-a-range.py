#
# @lc app=leetcode id=3869 lang=python3
#
# [3869] Count Fancy Numbers in a Range
#
# https://leetcode.com/problems/count-fancy-numbers-in-a-range/description/
#
# algorithms
# Hard (27.48%)
# Likes:    66
# Dislikes: 2
# Total Accepted:    5.4K
# Total Submissions: 19.7K
# Testcase Example:  "8\n10"
#
#
# You are given two integers l and r.
#
# An integer is called good if its digits form a strictly monotone
# sequence, meaning the digits are strictly increasing or strictly
# decreasing. All single-digit integers are considered good.
#
# An integer is called fancy if it is good, or if the sum of its digits is
# good.
#
# Return an integer representing the number of fancy integers in the range
# [l, r] (inclusive).
#
# A sequence is said to be strictly increasing if each element is strictly
# greater than its previous one (if exists).
#
# A sequence is said to be strictly decreasing if each element is strictly
# less than its previous one (if exists).
#
# Example 1:
#
# Input: l = 8, r = 10
#
# Output: 3
#
# Explanation:
#
# 8 and 9 are single-digit integers, so they are good and therefore fancy.
#
# 10 has digits [1, 0], which form a strictly decreasing sequence, so 10
# is good and thus fancy.
#
# Therefore, the answer is 3.
#
# Example 2:
#
# Input: l = 12340, r = 12341
#
# Output: 1
#
# Explanation:
#
# 12340
#
# 12340 is not good because [1, 2, 3, 4, 0] is not strictly monotone.
#
# The digit sum is 1 + 2 + 3 + 4 + 0 = 10.
#
# 10 is good as it has digits [1, 0], which is strictly decreasing.
# Therefore, 12340 is fancy.
#
# 12341
#
# 12341 is not good because [1, 2, 3, 4, 1] is not strictly monotone.
#
# The digit sum is 1 + 2 + 3 + 4 + 1 = 11.
#
# 11 is not good as it has digits [1, 1], which is not strictly monotone.
# Therefore, 12341 is not fancy.
#
# Therefore, the answer is 1.
#
# Example 3:
#
# Input: l = 123456788, r = 123456788
#
# Output: 0
#
# Explanation:
#
# 123456788 is not good because its digits are not strictly monotone.
#
# The digit sum is 1 + 2 + 3 + 4 + 5 + 6 + 7 + 8 + 8 = 44.
#
# 44 is not good as it has digits [4, 4], which is not strictly monotone.
# Therefore, 123456788 is not fancy.
#
# Therefore, the answer is 0.
#
# Constraints:
#
# 1 <= l <= r <= 10^15
#

# @lc code=start
from functools import cache


class Solution:
    def countFancy(self, l: int, r: int) -> int:
        """
        Interview explanation:
        Fancy = digits strictly monotone, or digit-sum is. Count with digit DP
        on [0, r] − [0, l − 1].

        Algorithm:
        - check(s): good digit-sum (no repeated digits for <100 via %11; for
          ≥100 only increasing 1ab form is possible).
        - dfs(pos, sum, prev, st, lim): st tracks mono state (0/1/2/3).
        - At end: st≠3 → good; else check(sum).

        Complexity: O(D^3 log^2 r) with memo, D=10.
        """
        def check(s: int) -> bool:
            if s < 100:
                return s % 11 != 0
            return 1 < (s // 10) % 10 < s % 10

        def calc(x: int) -> int:
            num = str(x)

            @cache
            def dfs(pos: int, s: int, prev: int, st: int, lim: bool) -> int:
                if pos >= len(num):
                    return 1 if st != 3 else int(check(s))
                up = int(num[pos]) if lim else 9
                res = 0
                for i in range(up + 1):
                    if st == 0:
                        if prev == 0:
                            nxt = 0
                        elif i > prev:
                            nxt = 1
                        elif i < prev:
                            nxt = 2
                        else:
                            nxt = 3
                    elif st == 1:
                        nxt = 1 if i > prev else 3
                    elif st == 2:
                        nxt = 2 if i < prev else 3
                    else:
                        nxt = 3
                    res += dfs(pos + 1, s + i, i, nxt, lim and i == up)
                return res

            return dfs(0, 0, 0, 0, True)

        return calc(r) - calc(l - 1)
# @lc code=end
