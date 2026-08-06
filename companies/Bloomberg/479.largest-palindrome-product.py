#
# @lc app=leetcode id=479 lang=python3
#
# [479] Largest Palindrome Product
#
# https://leetcode.com/problems/largest-palindrome-product/description/
#
# algorithms
# Hard (39.54%)
# Likes:    196
# Dislikes: 1569
# Total Accepted:    36.4K
# Total Submissions: 92.1K
# Testcase Example:  "2"
#
# Given an integer n, return the largest palindromic integer that can be
# represented as the product of two n-digits integers. Since the answer can be
# very large, return it modulo 1337.
#
# Example 1:
#
# Input: n = 2
# Output: 987
# Explanation: 99 x 91 = 9009, 9009 % 1337 = 987
#
# Example 2:
#
# Input: n = 1
# Output: 9
#
# Constraints:
#
# 1 <= n <= 8
#

# @lc code=start
class Solution:
    def largestPalindrome(self, n: int) -> int:
        """
        Interview explanation:
        Largest palindrome that is a product of two n-digit numbers, mod 1337.
        Generate palindromes from large to small (mirror first half) and check
        if any has an n-digit factor.

        Algorithm:
        - If n == 1: return 9.
        - upper = 10^n - 1; lower = 10^(n-1).
        - For first half from upper down: build palindrome; for factor from
          upper down to sqrt(pal), if divides and quotient is n-digit: return
          pal % 1337.

        Complexity: O(10^n * 10^{n/2}) worst theoretical; practical for n≤8.
        """
        if n == 1:
            return 9
        upper = 10**n - 1
        lower = 10 ** (n - 1)
        for left in range(upper, lower - 1, -1):
            s = str(left)
            pal = int(s + s[::-1])
            f = upper
            while f * f >= pal:
                if pal % f == 0:
                    other = pal // f
                    if lower <= other <= upper:
                        return pal % 1337
                f -= 1
        return 0
# @lc code=end
