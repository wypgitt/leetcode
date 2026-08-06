#
# @lc app=leetcode id=3744 lang=python3
#
# [3744] Find Kth Character in Expanded String
#
# https://leetcode.com/problems/find-kth-character-in-expanded-string/description/
#
# algorithms
# Medium (57.05%)
# Likes:    5
# Dislikes: 3
# Total Accepted:    583
# Total Submissions: 1K
# Testcase Example:  "\"hello world\"\n0"
#
#
# You are given a string s consisting of one or more words separated by
# single spaces. Each word in s consists of lowercase English letters.
#
# We obtain the expanded string t from s as follows:
#
# For each word in s, repeat its first character once, then its second
# character twice, and so on.
#
# For example, if s = "hello world", then t = "heelllllllooooo
# woorrrllllddddd".
#
# You are also given an integer k, representing a valid index of the
# string t.
#
# Return the k^th character of the string t.
#
# Example 1:
#
# Input: s = "hello world", k = 0
#
# Output: "h"
#
# Explanation:
#
# t = "heelllllllooooo woorrrllllddddd". Therefore, the answer is t[0] =
# "h".
#
# Example 2:
#
# Input: s = "hello world", k = 15
#
# Output: " "
#
# Explanation:
#
# t = "heelllllllooooo woorrrllllddddd". Therefore, the answer is t[15] =
# " ".
#
# Constraints:
#
# 1 <= s.length <= 10^5
#
# s contains only lowercase English letters and spaces ' '.
#
# s does not contain any leading or trailing spaces.
#
# All the words in s are separated by a single space.
#
# 0 <= k < t.length. That is, k is a valid index of t.
#

# @lc code=start
class Solution:
    def kthCharacter(self, s: str, k: int) -> str:
        """
        Interview explanation:
        Each word expands so the j-th letter (1-indexed in the word) repeats j
        times; spaces stay single. Find t[k] without building t.

        Algorithm:
        - Scan s; track position within the current word. Subtract the expanded
          length of each character (or 1 for space) from k until it goes negative.

        Complexity: O(|s|) time, O(1) space.
        """
        pos_in_word = 0
        for ch in s:
            if ch == " ":
                pos_in_word = 0
                k -= 1
            else:
                pos_in_word += 1
                k -= pos_in_word
            if k < 0:
                return ch
        return s[-1]
# @lc code=end
