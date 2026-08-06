#
# @lc app=leetcode id=680 lang=python3
#
# [680] Valid Palindrome II
#
# https://leetcode.com/problems/valid-palindrome-ii/description/
#
# algorithms
# Easy (44.56%)
# Likes:    9112
# Dislikes: 521
# Total Accepted:    1.2M
# Total Submissions: 2.7M
# Testcase Example:  "\"aba\""
#
# Given a string s, return true if the s can be palindrome after deleting at
# most one character from it.
#
# Example 1:
#
# Input: s = "aba"
# Output: true
#
# Example 2:
#
# Input: s = "abca"
# Output: true
# Explanation: You could delete the character 'c'.
#
# Example 3:
#
# Input: s = "abc"
# Output: false
#
# Constraints:
#
# 1 <= s.length <= 10^5
#
# s consists of lowercase English letters.
#

# @lc code=start
class Solution:
    def validPalindrome(self, s: str) -> bool:
        """
        Interview explanation:
        Check if s can become a palindrome by deleting at most one character.
        Two pointers; on first mismatch, try skipping left or right once.

        Algorithm:
        - i, j inward. On s[i]!=s[j], return is_pal(i+1,j) or is_pal(i,j-1).

        Complexity: O(n) time, O(1) space.
        """
        def is_pal(l: int, r: int) -> bool:
            while l < r:
                if s[l] != s[r]:
                    return False
                l += 1
                r -= 1
            return True

        i, j = 0, len(s) - 1
        while i < j:
            if s[i] != s[j]:
                return is_pal(i + 1, j) or is_pal(i, j - 1)
            i += 1
            j -= 1
        return True
# @lc code=end
