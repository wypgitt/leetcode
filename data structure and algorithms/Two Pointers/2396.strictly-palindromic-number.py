#
# @lc app=leetcode id=2396 lang=python3
#
# [2396] Strictly Palindromic Number
#
# https://leetcode.com/problems/strictly-palindromic-number/description/
#
# algorithms
# Medium (90.37%)
# Likes:    841
# Dislikes: 1779
# Total Accepted:    193.5K
# Total Submissions: 214.1K
# Testcase Example:  "9"
#
# An integer n is strictly palindromic if, for every base b between 2 and n - 2
# (inclusive), the string representation of the integer n in base b is
# palindromic.
#
# Given an integer n, return true if n is strictly palindromic and false
# otherwise.
#
# A string is palindromic if it reads the same forward and backward.
#
#
#
# Example 1:
#
# Input: n = 9
# Output: false
# Explanation: In base 2: 9 = 1001 (base 2), which is palindromic.
# In base 3: 9 = 100 (base 3), which is not palindromic.
# Therefore, 9 is not strictly palindromic so we return false.
# Note that in bases 4, 5, 6, and 7, n = 9 is also not palindromic.
#
# Example 2:
#
# Input: n = 4
# Output: false
# Explanation: We only consider base 2: 4 = 100 (base 2), which is not
# palindromic.
# Therefore, we return false.
#
#
#
# Constraints:
#
#
# 4 <= n <= 10^5
#

# @lc code=start

class Solution:
    def isStrictlyPalindromic(self, n: int) -> bool:
        """
        Interview explanation:
        n is strictly palindromic if for every base b in [2, n-2], its
        representation in base b is a palindrome. Prove/return whether n is.

        Algorithm:
        - For n >= 4, in base n-2 representation is always [1, 2] which is not
          a palindrome. n=1..3 have empty/invalid base ranges -> vacuously? but
          constraints n>=4. So always False.

        Complexity: O(1) time, O(1) space.
        """
        return False

    def isStrictlyPalindromic_math(self, n: int) -> bool:
        """
        Interview explanation:
        Alternate: explicitly check all bases (still False for n>=4).

        Algorithm:
        - For each base, convert and check palindrome.

        Complexity: O(n log n) time, O(log n) space.
        """
        def is_pal(n: int, b: int) -> bool:
            digits = []
            x = n
            while x:
                digits.append(x % b)
                x //= b
            return digits == digits[::-1]

        return all(is_pal(n, b) for b in range(2, n - 1))
# @lc code=end
