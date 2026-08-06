#
# @lc app=leetcode id=557 lang=python3
#
# [557] Reverse Words in a String III
#
# https://leetcode.com/problems/reverse-words-in-a-string-iii/description/
#
# algorithms
# Easy (84.11%)
# Likes:    6257
# Dislikes: 256
# Total Accepted:    1.2M
# Total Submissions: 1.4M
# Testcase Example:  "\"Let's take LeetCode contest\""
#
# Given a string s, reverse the order of characters in each word within a
# sentence while still preserving whitespace and initial word order.
#
# Example 1:
#
# Input: s = "Let's take LeetCode contest"
# Output: "s'teL ekat edoCteeL tsetnoc"
#
# Example 2:
#
# Input: s = "Mr Ding"
# Output: "rM gniD"
#
# Constraints:
#
# 1 <= s.length <= 5 * 10^4
#
# s contains printable ASCII characters.
#
# s does not contain any leading or trailing spaces.
#
# There is at least one word in s.
#
# All the words in s are separated by a single space.
#

# @lc code=start
class Solution:
    def reverseWords(self, s: str) -> str:
        """
        Interview explanation:
        Reverse each whitespace-separated word in place of its slot; keep
        word order and spaces.

        Algorithm:
        - Split on spaces, reverse each word, join with spaces.

        Complexity: O(n) time, O(n) space.
        """
        return " ".join(word[::-1] for word in s.split(" "))
# @lc code=end

