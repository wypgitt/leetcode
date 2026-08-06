#
# @lc app=leetcode id=3345 lang=python3
#
# [3345] Smallest Divisible Digit Product I
#
# https://leetcode.com/problems/smallest-divisible-digit-product-i/description/
#
# algorithms
# Easy (69.54%)
# Likes:    142
# Dislikes: 16
# Total Accepted:    74.7K
# Total Submissions: 107.4K
# Testcase Example:  "10\n2"
#
#
# You are given two integers n and t. Return the smallest number greater
# than or equal to n such that the product of its digits is divisible by
# t.
#
# Example 1:
#
# Input: n = 10, t = 2
#
# Output: 10
#
# Explanation:
#
# The digit product of 10 is 0, which is divisible by 2, making it the
# smallest number greater than or equal to 10 that satisfies the
# condition.
#
# Example 2:
#
# Input: n = 15, t = 3
#
# Output: 16
#
# Explanation:
#
# The digit product of 16 is 6, which is divisible by 3, making it the
# smallest number greater than or equal to 15 that satisfies the
# condition.
#
# Constraints:
#
# 1 <= n <= 100
#
# 1 <= t <= 10
#

# @lc code=start

class Solution:
    def smallestNumber(self, n: int, t: int) -> int:
        """
        Interview explanation:
        Find the smallest integer ≥ n whose digit product is divisible by t.
        n ≤ 100 and t ≤ 10 → brute-force from n upward.

        Algorithm:
        - For x = n, n+1, ... compute digit product; return first with prod % t == 0.
        - Any number containing 0 works for any t.

        Complexity: O(gap * digits) time, O(1) space; gap is tiny under constraints.
        """
        def product(x: int) -> int:
            p = 1
            for ch in str(x):
                p *= int(ch)
            return p

        while product(n) % t != 0:
            n += 1
        return n

    def smallestNumber_loop(self, n: int, t: int) -> int:
        """
        Interview explanation:
        Alternate digit extraction without strings.

        Algorithm:
        - Same scan; multiply digits via x % 10 / x // 10.

        Complexity: O(gap * digits) time, O(1) space.
        """
        x = n
        while True:
            p, y = 1, x
            while y:
                p *= y % 10
                y //= 10
            if p % t == 0:
                return x
            x += 1
# @lc code=end
