#
# @lc app=leetcode id=2278 lang=python3
#
# [2278] Percentage of Letter in String
#
# https://leetcode.com/problems/percentage-of-letter-in-string/description/
#
# algorithms
# Easy (75.29%)
# Likes:    567
# Dislikes: 64
# Total Accepted:    105.3K
# Total Submissions: 139.8K
# Testcase Example:  "\"foobar\"\n\"o\""
#
# Given a string s and a character letter, return the percentage of characters
# in s that equal letter rounded down to the nearest whole percent.
#
#
#
# Example 1:
#
# Input: s = "foobar", letter = "o"
# Output: 33
# Explanation:
# The percentage of characters in s that equal the letter 'o' is 2 / 6 * 100% =
# 33% when rounded down, so we return 33.
#
# Example 2:
#
# Input: s = "jjjj", letter = "k"
# Output: 0
# Explanation:
# The percentage of characters in s that equal the letter 'k' is 0%, so we
# return 0.
#
#
#
# Constraints:
#
#
# 1 <= s.length <= 100
#
#
# s consists of lowercase English letters.
#
#
# letter is a lowercase English letter.
#

# @lc code=start
class Solution:
    def percentageLetter(self, s: str, letter: str) -> int:
        """
        Interview explanation:
        Floor percentage of characters in s equal to letter.

        Algorithm:
        - 100 * count(letter) // len(s).

        Complexity: O(n) time, O(1) space.
        """
        return 100 * s.count(letter) // len(s)
# @lc code=end
