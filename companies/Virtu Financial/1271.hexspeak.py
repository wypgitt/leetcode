#
# @lc app=leetcode id=1271 lang=python3
#
# [1271] Hexspeak
#
# https://leetcode.com/problems/hexspeak/description/
#
# algorithms
# Easy (58.35%)
# Likes:    80
# Dislikes: 127
# Total Accepted:    13.3K
# Total Submissions: 22.8K
# Testcase Example:  "\"257\""
#
#
# A decimal number can be converted to its Hexspeak representation by
# first converting it to an uppercase hexadecimal string, then replacing
# all occurrences of the digit '0' with the letter 'O', and the digit '1'
# with the letter 'I'. Such a representation is valid if and only if it
# consists only of the letters in the set {'A', 'B', 'C', 'D', 'E', 'F',
# 'I', 'O'}.
#
# Given a string num representing a decimal integer n, return the Hexspeak
# representation of n if it is valid, otherwise return "ERROR".
#
# Example 1:
#
# Input: num = "257"
# Output: "IOI"
# Explanation: 257 is 101 in hexadecimal.
#
# Example 2:
#
# Input: num = "3"
# Output: "ERROR"
#
# Constraints:
#
# 1 <= num.length <= 12
#
# num does not contain leading zeros.
#
# num represents an integer in the range [1, 10^12].
#
# @lc code=start

class Solution:
    def toHexspeak(self, num: str) -> str:
        """
        Interview explanation:
        Premium. Convert decimal string to hex uppercase; letters O/I allowed
        for 0/1; if any other digit remains, return "ERROR".

        Algorithm:
        - h = format(int(num), 'X'); replace '0'->'O', '1'->'I'.
        - If any char not in A-F,O,I: ERROR else return h.

        Complexity: O(log num) time/space.
        """
        h = format(int(num), "X").replace("0", "O").replace("1", "I")
        allowed = set("ABCDEFIO")
        for ch in h:
            if ch not in allowed:
                return "ERROR"
        return h
# @lc code=end
