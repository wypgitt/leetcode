#
# @lc app=leetcode id=2000 lang=python3
#
# [2000] Reverse Prefix of Word
#
# https://leetcode.com/problems/reverse-prefix-of-word/description/
#
# algorithms
# Easy (86.5%)
# Likes:    1539
# Dislikes: 46
# Total Accepted:    398K
# Total Submissions: 460K
# Testcase Example:  "\"abcdefd\""
#
# Given a 0-indexed string word and a character ch, reverse the segment of word
# that starts at index 0 and ends at the index of the first occurrence of ch
# (inclusive). If the character ch does not exist in word, do nothing.
#
# For example, if word = "abcdefd" and ch = "d", then you should reverse the
# segment that starts at 0 and ends at 3 (inclusive). The resulting string will
# be "dcbaefd".
#
# Return the resulting string.
#
# Example 1:
#
# Input: word = "abcdefd", ch = "d"
# Output: "dcbaefd"
# Explanation: The first occurrence of "d" is at index 3.
# Reverse the part of word from 0 to 3 (inclusive), the resulting string is
# "dcbaefd".
#
# Example 2:
#
# Input: word = "xyxzxe", ch = "z"
# Output: "zxyxxe"
# Explanation: The first and only occurrence of "z" is at index 3.
# Reverse the part of word from 0 to 3 (inclusive), the resulting string is
# "zxyxxe".
#
# Example 3:
#
# Input: word = "abcd", ch = "z"
# Output: "abcd"
# Explanation: "z" does not exist in word.
# You should not do any reverse operation, the resulting string is "abcd".
#
# Constraints:
#
# 1 <= word.length <= 250
#
# word consists of lowercase English letters.
#
# ch is a lowercase English letter.
#

# @lc code=start
class Solution:
    def reversePrefix(self, word: str, ch: str) -> str:
        """
        Interview explanation:
        Reverse the prefix of word ending at the first occurrence of ch; if ch
        absent, return word unchanged.

        Algorithm:
        - i = word.find(ch); if i<0 return word; else reverse word[:i+1]+rest.

        Complexity: O(n) time, O(n) space.
        """
        i = word.find(ch)
        if i < 0:
            return word
        return word[: i + 1][::-1] + word[i + 1 :]

    def reversePrefix_two_pointer(self, word: str, ch: str) -> str:
        """
        Interview explanation:
        Alternate: locate ch then two-pointer reverse into a list.

        Algorithm:
        - Find index; list(word); reverse segment [0..i]; join.

        Complexity: O(n) time, O(n) space.
        """
        chars = list(word)
        i = 0
        while i < len(chars) and chars[i] != ch:
            i += 1
        if i == len(chars):
            return word
        l, r = 0, i
        while l < r:
            chars[l], chars[r] = chars[r], chars[l]
            l += 1
            r -= 1
        return "".join(chars)
# @lc code=end

