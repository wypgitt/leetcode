#
# @lc app=leetcode id=3260 lang=python3
#
# [3260] Find the Largest Palindrome Divisible by K
#
# https://leetcode.com/problems/find-the-largest-palindrome-divisible-by-k/description/
#
# algorithms
# Hard (17.10%)
# Likes:    112
# Dislikes: 70
# Total Accepted:    9.7K
# Total Submissions: 56.5K
# Testcase Example:  "3\n5"
#
#
# You are given two positive integers n and k.
#
# An integer x is called k-palindromic if:
#
# x is a palindrome.
#
# x is divisible by k.
#
# Return the largest integer having n digits (as a string) that is
# k-palindromic.
#
# Note that the integer must not have leading zeros.
#
# Example 1:
#
# Input: n = 3, k = 5
#
# Output: "595"
#
# Explanation:
#
# 595 is the largest k-palindromic integer with 3 digits.
#
# Example 2:
#
# Input: n = 1, k = 4
#
# Output: "8"
#
# Explanation:
#
# 4 and 8 are the only k-palindromic integers with 1 digit.
#
# Example 3:
#
# Input: n = 5, k = 6
#
# Output: "89898"
#
# Constraints:
#
# 1 <= n <= 10^5
#
# 1 <= k <= 9
#

# @lc code=start
class Solution:
    def largestPalindrome(self, n: int, k: int) -> str:
        """
        Interview explanation:
        Build the largest n-digit palindrome divisible by k (k <= 9). Divisibility
        rules for 1..9 yield closed forms; fill as many 9s as possible and adjust
        border/middle digits for the modulus.

        Algorithm:
        - Case on k using divisibility (last digits for 2/4/5/8, digit-sum for
          3/9, combine for 6, period-12 pattern for 7).
        - Return the constructed digit string (no leading zeros).

        Complexity: O(n) time and space.
        """
        if k in (1, 3, 9):
            return "9" * n
        if k == 2:
            return "8" * n if n <= 2 else "8" + "9" * (n - 2) + "8"
        if k == 4:
            return "8" * n if n <= 4 else "88" + "9" * (n - 4) + "88"
        if k == 5:
            return "5" * n if n <= 2 else "5" + "9" * (n - 2) + "5"
        if k == 6:
            if n <= 2:
                return "6" * n
            if n % 2 == 1:
                l = n // 2 - 1
                return "8" + "9" * l + "8" + "9" * l + "8"
            l = n // 2 - 2
            return "8" + "9" * l + "77" + "9" * l + "8"
        if k == 8:
            return "8" * n if n <= 6 else "888" + "9" * (n - 6) + "888"
        # k == 7: largest palindrome of 9s adjusted on a 12-length period
        middle = {
            0: "",
            1: "7",
            2: "77",
            3: "959",
            4: "9779",
            5: "99799",
            6: "999999",
            7: "9994999",
            8: "99944999",
            9: "999969999",
            10: "9999449999",
            11: "99999499999",
        }
        q, r = divmod(n, 12)
        return "999999" * q + middle[r] + "999999" * q
# @lc code=end
