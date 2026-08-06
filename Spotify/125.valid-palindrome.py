#
# @lc app=leetcode id=125 lang=python3
#
# [125] Valid Palindrome
#
# https://leetcode.com/problems/valid-palindrome/description/
#
# algorithms
# Easy (53.98%)
# Likes:    11893
# Dislikes: 8658
# Total Accepted:    5.8M
# Total Submissions: 11M
# Testcase Example:  "\"A man, a plan, a canal: Panama\""
#
# A phrase is a palindrome if, after converting all uppercase letters into
# lowercase letters and removing all non-alphanumeric characters, it reads the
# same forward and backward. Alphanumeric characters include letters and
# numbers.
#
# Given a string s, return true if it is a palindrome, or false otherwise.
#
# Example 1:
#
# Input: s = "A man, a plan, a canal: Panama"
# Output: true
# Explanation: "amanaplanacanalpanama" is a palindrome.
#
# Example 2:
#
# Input: s = "race a car"
# Output: false
# Explanation: "raceacar" is not a palindrome.
#
# Example 3:
#
# Input: s = " "
# Output: true
# Explanation: s is an empty string "" after removing non-alphanumeric
# characters.
# Since an empty string reads the same forward and backward, it is a
# palindrome.
#
# Constraints:
#
# 1 <= s.length <= 2 * 10^5
#
# s consists only of printable ASCII characters.
#

# @lc code=start
class Solution:
    def isPalindrome(self, s: str) -> bool:
        """
        Interview explanation:
        Compare characters from both ends, skipping non-alphanumeric chars and
        ignoring case. Two pointers use O(1) extra space.

        Algorithm:
        - left starts at 0, right at len(s)-1.
        - Advance past non-alphanumeric characters.
        - Compare lowercased chars; mismatch -> False; otherwise move inward.

        Complexity: O(n) time, O(1) space.
        """
        left, right = 0, len(s) - 1
        while left < right:
            while left < right and not s[left].isalnum():
                left += 1
            while left < right and not s[right].isalnum():
                right -= 1
            if s[left].lower() != s[right].lower():
                return False
            left += 1
            right -= 1
        return True
# @lc code=end
