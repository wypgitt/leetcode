#
# @lc app=leetcode id=906 lang=python3
#
# [906] Super Palindromes
#
# https://leetcode.com/problems/super-palindromes/description/
#
# algorithms
# Hard (40.21%)
# Likes:    379
# Dislikes: 423
# Total Accepted:    29.4K
# Total Submissions: 73.1K
# Testcase Example:  "\"4\""
#
# Let's say a positive integer is a super-palindrome if it is a palindrome, and
# it is also the square of a palindrome.
#
# Given two positive integers left and right represented as strings, return the
# number of super-palindromes integers in the inclusive range [left, right].
#
# Example 1:
#
# Input: left = "4", right = "1000"
# Output: 4
# Explanation: 4, 9, 121, and 484 are superpalindromes.
# Note that 676 is not a superpalindrome: 26 * 26 = 676, but 26 is not a
# palindrome.
#
# Example 2:
#
# Input: left = "1", right = "2"
# Output: 1
#
# Constraints:
#
# 1 <= left.length, right.length <= 18
#
# left and right consist of only digits.
#
# left and right cannot have leading zeros.
#
# left and right represent integers in the range [1, 10^18 - 1].
#
# left is less than or equal to right.
#

# @lc code=start
class Solution:
    def superpalindromesInRange(self, left: str, right: str) -> int:
        """
        Interview explanation:
        Super-palindrome: palindrome whose square root is also a palindrome.
        Enumerate palindromic roots up to 1e9 (since right <= 1e18), square them,
        and count those in [left, right] that are palindromes.

        Algorithm:
        - For i in 1..1e5-1: build odd-length palindrome (s + reverse(s[:-1]))
          and even-length (s + reverse(s)); sq = p*p; check range + palindrome.

        Complexity: O(W * log R) with W ≈ 2e5 candidates; O(1) extra space.
        """
        L, R = int(left), int(right)
        ans = 0

        def is_pal(x: int) -> bool:
            s = str(x)
            return s == s[::-1]

        for i in range(1, 100000):
            s = str(i)
            for p in (int(s + s[-2::-1]), int(s + s[::-1])):
                if p > 10**9:
                    continue
                sq = p * p
                if sq > R:
                    continue
                if sq >= L and is_pal(sq):
                    ans += 1
        return ans
# @lc code=end
