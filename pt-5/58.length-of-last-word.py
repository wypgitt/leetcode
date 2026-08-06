#
# @lc app=leetcode id=58 lang=python3
#
# [58] Length of Last Word
#
# https://leetcode.com/problems/length-of-last-word/description/
#
# algorithms
# Easy (59.43%)
# Likes:    6547
# Dislikes: 365
# Total Accepted:    3.6M
# Total Submissions: 6.1M
# Testcase Example:  "\"Hello World\""
#
# Given a string s consisting of words and spaces, return the length of the
# last word in the string.
#
# A word is a maximal substring consisting of non-space characters only.
#
# Example 1:
#
# Input: s = "Hello World"
# Output: 5
# Explanation: The last word is "World" with length 5.
#
# Example 2:
#
# Input: s = " fly me to the moon "
# Output: 4
# Explanation: The last word is "moon" with length 4.
#
# Example 3:
#
# Input: s = "luffy is still joyboy"
# Output: 6
# Explanation: The last word is "joyboy" with length 6.
#
# Constraints:
#
# 1 <= s.length <= 10^4
#
# s consists of only English letters and spaces ' '.
#
# There will be at least one word in s.
#

# @lc code=start
class Solution:
    def lengthOfLastWord(self, s: str) -> int:
        """
        Interview explanation:
        Words are maximal non-space substrings. Trailing spaces are allowed, so
        scanning from the end avoids trimming the whole string.

        Algorithm:
        - Start at the last index; skip trailing spaces.
        - Count consecutive non-space characters until a space or start.
        - Return that count.

        Complexity: O(n) time, O(1) space.
        """
        i = len(s) - 1
        while i >= 0 and s[i] == ' ':
            i -= 1

        length = 0
        while i >= 0 and s[i] != ' ':
            length += 1
            i -= 1
        return length
# @lc code=end
