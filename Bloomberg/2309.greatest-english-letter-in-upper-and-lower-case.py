#
# @lc app=leetcode id=2309 lang=python3
#
# [2309] Greatest English Letter in Upper and Lower Case
#
# https://leetcode.com/problems/greatest-english-letter-in-upper-and-lower-case/description/
#
# algorithms
# Easy (72.76%)
# Likes:    535
# Dislikes: 33
# Total Accepted:    78.4K
# Total Submissions: 107.8K
# Testcase Example:  "\"lEeTcOdE\""
#
# Given a string of English letters s, return the greatest English letter which
# occurs as both a lowercase and uppercase letter in s. The returned letter
# should be in uppercase. If no such letter exists, return an empty string.
#
# An English letter b is greater than another letter a if b appears after a in
# the English alphabet.
#
#
#
# Example 1:
#
# Input: s = "lEeTcOdE"
# Output: "E"
# Explanation:
# The letter 'E' is the only letter to appear in both lower and upper case.
#
# Example 2:
#
# Input: s = "arRAzFif"
# Output: "R"
# Explanation:
# The letter 'R' is the greatest letter to appear in both lower and upper case.
# Note that 'A' and 'F' also appear in both lower and upper case, but 'R' is
# greater than 'F' or 'A'.
#
# Example 3:
#
# Input: s = "AbCdEfGhIjK"
# Output: ""
# Explanation:
# There is no letter that appears in both lower and upper case.
#
#
#
# Constraints:
#
#
# 1 <= s.length <= 1000
#
#
# s consists of lowercase and uppercase English letters.
#

# @lc code=start
class Solution:
    def greatestLetter(self, s: str) -> str:
        """
        Interview explanation:
        Among letters appearing in both lowercase and uppercase forms, return
        the greatest uppercase letter; else "".

        Algorithm:
        - Put all chars in a set; scan Z..A for letter with both cases present.

        Complexity: O(n) time, O(1) space (alphabet).
        """
        seen = set(s)
        for c in range(ord('Z'), ord('A') - 1, -1):
            ch = chr(c)
            if ch in seen and ch.lower() in seen:
                return ch
        return ""
# @lc code=end
