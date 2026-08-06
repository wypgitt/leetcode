#
# @lc app=leetcode id=1842 lang=python3
#
# [1842] Next Palindrome Using Same Digits
#
# https://leetcode.com/problems/next-palindrome-using-same-digits/description/
#
# algorithms
# Hard (54.18%)
# Likes:    126
# Dislikes: 19
# Total Accepted:    7.1K
# Total Submissions: 13.2K
# Testcase Example:  "\"1221\""
#
#
# You are given a numeric string num, representing a very large
# palindrome.
#
# Return the smallest palindrome larger than num that can be created by
# rearranging its digits. If no such palindrome exists, return an empty
# string "".
#
# A palindrome is a number that reads the same backward as forward.
#
# Example 1:
#
# Input: num = "1221"
# Output: "2112"
# Explanation: The next palindrome larger than "1221" is "2112".
#
# Example 2:
#
# Input: num = "32123"
# Output: ""
# Explanation: No palindromes larger than "32123" can be made by
# rearranging the digits.
#
# Example 3:
#
# Input: num = "45544554"
# Output: "54455445"
# Explanation: The next palindrome larger than "45544554" is "54455445".
#
# Constraints:
#
# 1 <= num.length <= 10^5
#
# num is a palindrome.
#
# @lc code=start
class Solution:
    def nextPalindrome(self, num: str) -> str:
        """
        Interview explanation:
        Premium: next lexicographically larger palindrome using same digits, or "".
        Next-permutation the first half, then mirror.

        Algorithm (next perm of half + mirror):
        - half = num[:n//2]; next_permutation(half); if none return "";
          mirror with middle if odd length.

        Complexity: O(n) time, O(n) space.
        """
        n = len(num)
        half = list(num[: n // 2])
        mid = num[n // 2] if n % 2 else ''

        def next_permutation(a: list) -> bool:
            i = len(a) - 2
            while i >= 0 and a[i] >= a[i + 1]:
                i -= 1
            if i < 0:
                return False
            j = len(a) - 1
            while a[j] <= a[i]:
                j -= 1
            a[i], a[j] = a[j], a[i]
            a[i + 1:] = reversed(a[i + 1:])
            return True

        if not next_permutation(half):
            return ""
        left = ''.join(half)
        return left + mid + left[::-1]
# @lc code=end
