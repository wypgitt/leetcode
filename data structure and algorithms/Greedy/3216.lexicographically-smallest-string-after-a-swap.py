#
# @lc app=leetcode id=3216 lang=python3
#
# [3216] Lexicographically Smallest String After a Swap
#
# https://leetcode.com/problems/lexicographically-smallest-string-after-a-swap/description/
#
# algorithms
# Easy (54.83%)
# Likes:    103
# Dislikes: 32
# Total Accepted:    56.8K
# Total Submissions: 103.6K
# Testcase Example:  "\"45320\""
#
#
# Given a string s containing only digits, return the lexicographically
# smallest string that can be obtained after swapping adjacent digits in s
# with the same parity at most once.
#
# Digits have the same parity if both are odd or both are even. For
# example, 5 and 9, as well as 2 and 4, have the same parity, while 6 and
# 9 do not.
#
# Example 1:
#
# Input: s = "45320"
#
# Output: "43520"
#
# Explanation:
#
# s[1] == '5' and s[2] == '3' both have the same parity, and swapping them
# results in the lexicographically smallest string.
#
# Example 2:
#
# Input: s = "001"
#
# Output: "001"
#
# Explanation:
#
# There is no need to perform a swap because s is already the
# lexicographically smallest.
#
# Constraints:
#
# 2 <= s.length <= 100
#
# s consists only of digits.
#

# @lc code=start
class Solution:
    def getSmallestString(self, s: str) -> str:
        """
        Interview explanation:
        At most one swap of adjacent digits with the same parity (both odd or
        both even). Choose the leftmost improving swap for lex-smallest result.

        Algorithm:
        - Scan i from 0..n-2; if s[i] and s[i+1] same parity and s[i] > s[i+1],
          swap and stop.

        Complexity: O(n) time, O(n) space for the character list.
        """
        chars = list(s)
        for i in range(len(chars) - 1):
            if (ord(chars[i]) % 2 == ord(chars[i + 1]) % 2) and chars[i] > chars[i + 1]:
                chars[i], chars[i + 1] = chars[i + 1], chars[i]
                break
        return "".join(chars)
# @lc code=end
