#
# @lc app=leetcode id=1839 lang=python3
#
# [1839] Longest Substring Of All Vowels in Order
#
# https://leetcode.com/problems/longest-substring-of-all-vowels-in-order/description/
#
# algorithms
# Medium (52.17%)
# Likes:    866
# Dislikes: 31
# Total Accepted:    49.1K
# Total Submissions: 94.2K
# Testcase Example:  "\"aeiaaioaaaaeiiiiouuuooaauuaeiu\""
#
# A string is considered beautiful if it satisfies the following conditions:
#
# Each of the 5 English vowels ('a', 'e', 'i', 'o', 'u') must appear at least
# once in it.
#
# The letters must be sorted in alphabetical order (i.e. all 'a's before 'e's,
# all 'e's before 'i's, etc.).
#
# For example, strings "aeiou" and "aaaaaaeiiiioou" are considered beautiful,
# but "uaeio", "aeoiu", and "aaaeeeooo" are not beautiful.
#
# Given a string word consisting of English vowels, return the length of the
# longest beautiful substring of word. If no such substring exists, return 0.
#
# A substring is a contiguous sequence of characters in a string.
#
# Example 1:
#
# Input: word = "aeiaaioaaaaeiiiiouuuooaauuaeiu"
# Output: 13
# Explanation: The longest beautiful substring in word is "aaaaeiiiiouuu" of
# length 13.
#
# Example 2:
#
# Input: word = "aeeeiiiioooauuuaeiou"
# Output: 5
# Explanation: The longest beautiful substring in word is "aeiou" of length 5.
#
# Example 3:
#
# Input: word = "a"
# Output: 0
# Explanation: There is no beautiful substring, so return 0.
#
# Constraints:
#
# 1 <= word.length <= 5 * 10^5
#
# word consists of characters 'a', 'e', 'i', 'o', and 'u'.
#

# @lc code=start
class Solution:
    def longestBeautifulSubstring(self, word: str) -> int:
        """
        Interview explanation:
        Longest substring that is nondecreasing vowels a..u and contains all five.

        Algorithm (scan groups):
        - Track current streak length and unique vowel count; reset on decrease;
          update ans when 5 unique.

        Complexity: O(n) time, O(1) space.
        """
        ans = 0
        cnt = 1
        unique = 1
        for i in range(1, len(word)):
            if word[i] < word[i - 1]:
                cnt = 1
                unique = 1
            else:
                cnt += 1
                if word[i] != word[i - 1]:
                    unique += 1
            if unique == 5:
                ans = max(ans, cnt)
        return ans
# @lc code=end
