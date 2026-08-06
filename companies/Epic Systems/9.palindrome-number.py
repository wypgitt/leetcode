#
# @lc app=leetcode id=9 lang=python3
#
# [9] Palindrome Number
#
# https://leetcode.com/problems/palindrome-number/description/
#
# algorithms
# Easy (60.84%)
# Likes:    16156
# Dislikes: 2941
# Total Accepted:    8.6M
# Total Submissions: 14M
# Testcase Example:  "121"
#
# Given an integer x, return true if x is a palindrome, and false otherwise.
#
# Example 1:
#
# Input: x = 121
# Output: true
# Explanation: 121 reads as 121 from left to right and from right to left.
#
# Example 2:
#
# Input: x = -121
# Output: false
# Explanation: From left to right, it reads -121. From right to left, it
# becomes 121-. Therefore it is not a palindrome.
#
# Example 3:
#
# Input: x = 10
# Output: false
# Explanation: Reads 01 from right to left. Therefore it is not a palindrome.
#
# Constraints:
#
# -2^31 <= x <= 2^31 - 1
#
# Follow up: Could you solve it without converting the integer to a string?
#

# @lc code=start
class Solution:
    def isPalindrome(self, x: int) -> bool:
        """
        Interview explanation:
        Check whether an integer reads the same forwards and backwards without
        converting it to a string (follow-up constraint). Negatives are never
        palindromes because of the leading '-'.

        Algorithm:
        - If x < 0, return False.
        - If x ends with 0 and is not 0 itself, return False (e.g. 10 -> 01).
        - Reverse only the second half of the digits into `reverted`.
        - Stop when `x` has no more digits than `reverted` (x <= reverted).
        - Equal halves mean palindrome. For odd length, drop the middle digit
          of `reverted` with `reverted // 10` before comparing.

        Complexity: O(log10 x) time, O(1) space.
        """
        if x < 0 or (x % 10 == 0 and x != 0):
            return False

        reverted = 0
        while x > reverted:
            reverted = reverted * 10 + x % 10
            x //= 10

        return x == reverted or x == reverted // 10

    def isPalindromeString(self, x: int) -> bool:
        """
        Interview explanation:
        Convert the integer to a string and check if it equals its reverse.
        Simpler than reverse-half, but uses extra space and does not satisfy
        the follow-up.

        Algorithm:
        - Convert x to a string s.
        - Return whether s equals s[::-1].

        Complexity: O(log10 x) time, O(log10 x) space.
        """
        s = str(x)
        return s == s[::-1]
# @lc code=end
