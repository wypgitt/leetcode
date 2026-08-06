#
# @lc app=leetcode id=3747 lang=python3
#
# [3747] Count Distinct Integers After Removing Zeros
#
# https://leetcode.com/problems/count-distinct-integers-after-removing-zeros/description/
#
# algorithms
# Medium (23.16%)
# Likes:    127
# Dislikes: 10
# Total Accepted:    16.4K
# Total Submissions: 70.9K
# Testcase Example:  "10"
#
#
# You are given a positive integer n.
#
# For every integer x from 1 to n, we write down the integer obtained by
# removing all zeros from the decimal representation of x.
#
# Return an integer denoting the number of distinct integers written down.
#
# Example 1:
#
# Input: n = 10
#
# Output: 9
#
# Explanation:
#
# The integers we wrote down are 1, 2, 3, 4, 5, 6, 7, 8, 9, 1. There are 9
# distinct integers (1, 2, 3, 4, 5, 6, 7, 8, 9).
#
# Example 2:
#
# Input: n = 3
#
# Output: 3
#
# Explanation:
#
# The integers we wrote down are 1, 2, 3. There are 3 distinct integers
# (1, 2, 3).
#
# Constraints:
#
# 1 <= n <= 10^15
#

# @lc code=start
class Solution:
    def countDistinct(self, n: int) -> int:
        """
        Interview explanation:
        Removing zeros never increases a number, so distinct images for x in
        [1, n] equal the count of zero-free integers in [1, n].

        Algorithm:
        - Combinatorics on digits 1..9: add all shorter lengths, then walk n's
          digits; stop early if a 0 appears; include n if it is zero-free.

        Complexity: O(log n) time, O(1) space.
        """
        s = str(n)
        L = len(s)
        base = 9 ** L
        result = (base - 9) // 8  # 9 + 9^2 + ... + 9^(L-1)
        base //= 9
        for ch in s:
            if ch == "0":
                break
            result += (ord(ch) - ord("0") - 1) * base
            base //= 9
        else:
            result += 1
        return result

    def countDistinct_digit_dp(self, n: int) -> int:
        """
        Interview explanation:
        Alternate: digit DP counting numbers with no zero digits.

        Algorithm:
        - dfs(pos, started, tight); after starting, only place digits 1..9.

        Complexity: O(log n) time/space with memo.
        """
        from functools import cache

        digits = list(map(int, str(n)))

        @cache
        def dfs(pos: int, started: bool, tight: bool) -> int:
            if pos == len(digits):
                return int(started)
            up = digits[pos] if tight else 9
            ans = 0
            for d in range(up + 1):
                if not started:
                    if d == 0:
                        ans += dfs(pos + 1, False, tight and d == up)
                    else:
                        ans += dfs(pos + 1, True, tight and d == up)
                elif d != 0:
                    ans += dfs(pos + 1, True, tight and d == up)
            return ans

        return dfs(0, False, True)
# @lc code=end
