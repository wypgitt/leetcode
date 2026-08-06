#
# @lc app=leetcode id=3517 lang=python3
#
# [3517] Smallest Palindromic Rearrangement I
#
# https://leetcode.com/problems/smallest-palindromic-rearrangement-i/description/
#
# algorithms
# Medium (74.53%)
# Likes:    396
# Dislikes: 5
# Total Accepted:    183.9K
# Total Submissions: 246.8K
# Testcase Example:  "\"z\""
#
#
# You are given a palindromic string s.
#
# Return the lexicographically smallest palindromic permutation of s.
#
# Example 1:
#
# Input: s = "z"
#
# Output: "z"
#
# Explanation:
#
# A string of only one character is already the lexicographically smallest
# palindrome.
#
# Example 2:
#
# Input: s = "babab"
#
# Output: "abbba"
#
# Explanation:
#
# Rearranging "babab" → "abbba" gives the smallest lexicographic
# palindrome.
#
# Example 3:
#
# Input: s = "daccad"
#
# Output: "acddca"
#
# Explanation:
#
# Rearranging "daccad" → "acddca" gives the smallest lexicographic
# palindrome.
#
# Constraints:
#
# 1 <= s.length <= 10^5
#
# s consists of lowercase English letters.
#
# s is guaranteed to be palindromic.
#

# @lc code=start
import collections


class Solution:
    def smallestPalindrome(self, s: str) -> str:
        """
        Interview explanation:
        Build the lexicographically smallest palindrome anagram: smallest
        multiset half on the left, mirror on the right, odd char in the middle.

        Algorithm:
        - Count letters; left gets c*(freq//2) in alpha order; mid = odd letter.
        - Return left + mid + reverse(left).

        Complexity: O(n) time, O(1) extra space.
        """
        cnt = collections.Counter(s)
        left_parts = []
        mid = ""
        for c in "abcdefghijklmnopqrstuvwxyz":
            if cnt[c] % 2:
                mid = c
            left_parts.append(c * (cnt[c] // 2))
        left = "".join(left_parts)
        return left + mid + left[::-1]
# @lc code=end
