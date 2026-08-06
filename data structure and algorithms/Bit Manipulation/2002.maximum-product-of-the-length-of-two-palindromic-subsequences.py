#
# @lc app=leetcode id=2002 lang=python3
#
# [2002] Maximum Product of the Length of Two Palindromic Subsequences
#
# https://leetcode.com/problems/maximum-product-of-the-length-of-two-palindromic-subsequences/description/
#
# algorithms
# Medium (62.64%)
# Likes:    1023
# Dislikes: 91
# Total Accepted:    40.6K
# Total Submissions: 64.8K
# Testcase Example:  "\"leetcodecom\""
#
# Given a string s, find two disjoint palindromic subsequences of s such that
# the product of their lengths is maximized. The two subsequences are disjoint
# if they do not both pick a character at the same index.
#
# Return the maximum possible product of the lengths of the two palindromic
# subsequences.
#
# A subsequence is a string that can be derived from another string by deleting
# some or no characters without changing the order of the remaining characters.
# A string is palindromic if it reads the same forward and backward.
#
#
#
# Example 1:
#
# Input: s = "leetcodecom"
# Output: 9
# Explanation: An optimal solution is to choose "ete" for the 1^st subsequence
# and "cdc" for the 2^nd subsequence.
# The product of their lengths is: 3 * 3 = 9.
#
# Example 2:
#
# Input: s = "bb"
# Output: 1
# Explanation: An optimal solution is to choose "b" (the first character) for
# the 1^st subsequence and "b" (the second character) for the 2^nd subsequence.
# The product of their lengths is: 1 * 1 = 1.
#
# Example 3:
#
# Input: s = "accbcaxxcxx"
# Output: 25
# Explanation: An optimal solution is to choose "accca" for the 1^st subsequence
# and "xxcxx" for the 2^nd subsequence.
# The product of their lengths is: 5 * 5 = 25.
#
#
#
# Constraints:
#
#
# 2 <= s.length <= 12
#
#
# s consists of lowercase English letters only.
#

# @lc code=start
class Solution:
    def maxProduct(self, s: str) -> int:
        """
        Interview explanation:
        Split characters into two disjoint subsequences that are both
        palindromes; maximize product of their lengths. n <= 12 → bitmask.

        Algorithm:
        - For every mask, check if selected chars form a palindrome; store length.
        - For every pair of disjoint masks, maximize len1 * len2.

        Complexity: O(2^n * n + 3^n) time with n<=12; O(2^n) space.
        """
        n = len(s)
        pal_len = [0] * (1 << n)
        for mask in range(1, 1 << n):
            chars = [s[i] for i in range(n) if mask & (1 << i)]
            if chars == chars[::-1]:
                pal_len[mask] = len(chars)
        ans = 0
        full = (1 << n) - 1
        for m1 in range(1, 1 << n):
            if not pal_len[m1]:
                continue
            rest = full ^ m1
            m2 = rest
            while m2:
                if pal_len[m2]:
                    ans = max(ans, pal_len[m1] * pal_len[m2])
                m2 = (m2 - 1) & rest
        return ans
# @lc code=end
