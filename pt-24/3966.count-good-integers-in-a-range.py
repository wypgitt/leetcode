#
# @lc app=leetcode id=3966 lang=python3
#
# [3966] Count Good Integers in a Range
#
# https://leetcode.com/problems/count-good-integers-in-a-range/description/
#
# algorithms
# Hard (52.19%)
# Likes:    41
# Dislikes: 1
# Total Accepted:    9.6K
# Total Submissions: 18.3K
# Testcase Example:  "10\n15\n1"
#
#
# You are given three integers l, r and k.
#
# A number is considered good if the absolute difference between every
# pair of adjacent digits is at most k.
#
# Return the number of good integers in the range [l, r] (inclusive).
#
# The absolute difference between values x and y is defined as abs(x - y).
#
# Example 1:
#
# Input: l = 10, r = 15, k = 1
#
# Output: 3
#
# Explanation:
#
# The good integers in the range are 10, 11, and 12.
#
# For 10, abs(1 - 0) = 1.
#
# For 11, abs(1 - 1) = 0.
#
# For 12, abs(1 - 2) = 1.
#
# All these differences are at most k = 1. Thus, the answer is 3.
#
# Example 2:
#
# Input: l = 201, r = 204, k = 2
#
# Output: 2
#
# Explanation:
#
# The good integers in the range are 201 and 202.
#
# For 201, abs(2 - 0) = 2 and abs(0 - 1) = 1.
#
# For 202, abs(2 - 0) = 2 and abs(0 - 2) = 2.
#
# Thus, the answer is 2.
#
# Constraints:
#
# 10 <= l <= r <= 10^15
#
# 0 <= k <= 9
#

# @lc code=start

from functools import cache


class Solution:
    def goodIntegers(self, l: int, r: int, k: int) -> int:
        """
        Interview explanation:
        Count numbers in [l, r] whose adjacent digits differ by at most k using
        digit DP with simultaneous lower/upper bounds.

        Algorithm:
        - Pad l with leading zeros to match len(str(r)).
        - DFS(pos, prev_digit, tight_low, tight_high); prev=-1 before the first
          real digit so leading zeros do not constrain adjacency.
        - Enumerate allowed digits in [lo, hi] and memoize.

        Complexity: O(D) states with D = O(log r), O(D) space.
        """
        n = len(str(r))
        diff = n - len(str(l))
        high = list(map(int, str(r)))
        low = list(map(int, str(l).zfill(n)))

        @cache
        def dfs(i: int, pre: int, limit_low: bool, limit_high: bool) -> int:
            if i == n:
                return 1
            lo = low[i] if limit_low else 0
            hi = high[i] if limit_high else 9
            res = 0
            if i < diff and limit_low:
                res += dfs(i + 1, -1, True, False)
            start = 1 if i < diff and limit_low else lo
            for d in range(start, hi + 1):
                if pre == -1 or abs(pre - d) <= k:
                    res += dfs(
                        i + 1,
                        d,
                        limit_low and d == lo,
                        limit_high and d == hi,
                    )
            return res

        return dfs(0, -1, True, True)
# @lc code=end
