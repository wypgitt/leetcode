#
# @lc app=leetcode id=1309 lang=python3
#
# [1309] Decrypt String from Alphabet to Integer Mapping
#
# https://leetcode.com/problems/decrypt-string-from-alphabet-to-integer-mapping/description/
#
# algorithms
# Easy (80.64%)
# Likes:    1616
# Dislikes: 120
# Total Accepted:    153K
# Total Submissions: 190K
# Testcase Example:  "\"10#11#12\""
#
# You are given a string s formed by digits and '#'. We want to map s to
# English lowercase characters as follows:
#
# Characters ('a' to 'i') are represented by ('1' to '9') respectively.
#
# Characters ('j' to 'z') are represented by ('10#' to '26#') respectively.
#
# Return the string formed after mapping.
#
# The test cases are generated so that a unique mapping will always exist.
#
# Example 1:
#
# Input: s = "10#11#12"
# Output: "jkab"
# Explanation: "j" -> "10#" , "k" -> "11#" , "a" -> "1" , "b" -> "2".
#
# Example 2:
#
# Input: s = "1326#"
# Output: "acz"
#
# Constraints:
#
# 1 <= s.length <= 1000
#
# s consists of digits and the '#' letter.
#
# s will be a valid string such that mapping is always possible.
#

# @lc code=start
class Solution:
    def freqAlphabets(self, s: str) -> str:
        """
        Interview explanation:
        Mapping: '1'..'9' -> a..i; '10#'..'26#' -> j..z. Scan right-to-left so
        '#' groups are unambiguous.

        Algorithm:
        - i from end: if s[i]=='#', take s[i-2:i] as number; else single digit.

        Complexity: O(n) time, O(n) space.
        """
        ans = []
        i = len(s) - 1
        while i >= 0:
            if s[i] == "#":
                num = int(s[i - 2 : i])
                ans.append(chr(ord("a") + num - 1))
                i -= 3
            else:
                ans.append(chr(ord("a") + int(s[i]) - 1))
                i -= 1
        return "".join(reversed(ans))
# @lc code=end

