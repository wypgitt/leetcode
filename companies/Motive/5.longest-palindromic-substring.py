#
# @lc app=leetcode id=5 lang=python3
#
# [5] Longest Palindromic Substring
#
# https://leetcode.com/problems/longest-palindromic-substring/description/
#
# algorithms
# Medium (37.77%)
# Likes:    32685
# Dislikes: 2014
# Total Accepted:    4.7M
# Total Submissions: 12.5M
# Testcase Example:  '"babad"'
#
# Given a string s, return the longest palindromic substring in s.
# 
# 
# Example 1:
# 
# 
# Input: s = "babad"
# Output: "bab"
# Explanation: "aba" is also a valid answer.
# 
# 
# Example 2:
# 
# 
# Input: s = "cbbd"
# Output: "bb"
# 
# 
# 
# Constraints:
# 
# 
# 1 <= s.length <= 1000
# s consist of only digits and English letters.
# 
# 
#

# @lc code=start
from typing import List, Optional
class Solution:
    def longestPalindrome(self, s: str) -> str:
        """
        Interview explanation:
        A palindrome is determined by its center. Expanding around each possible
        odd and even center avoids building a DP table while still checking all
        candidate palindromes. This is usually the cleanest interview solution:
        easy to prove, O(1) extra space, and fast enough for the constraints.

        Algorithm:
        - For every index i, expand from (i, i) for odd length and (i, i + 1)
          for even length.
        - Expansion stops at mismatch or boundary.
        - Keep the best [start, end] range seen.

        Edge cases and tests:
        - Single character returns itself.
        - Even palindrome like "cbbd" returns "bb".
        - Multiple valid answers like "babad" can return either "bab" or "aba".

        Complexity: O(n^2) time in the worst case, O(1) extra space.
        """
        def expand(left: int, right: int) -> tuple[int, int]:
            while left >= 0 and right < len(s) and s[left] == s[right]:
                left -= 1
                right += 1
            return left + 1, right - 1

        best_left = best_right = 0
        for i in range(len(s)):
            for left, right in (expand(i, i), expand(i, i + 1)):
                if right - left > best_right - best_left:
                    best_left, best_right = left, right

        return s[best_left:best_right + 1]
# @lc code=end


