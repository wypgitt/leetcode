#
# @lc app=leetcode id=168 lang=python3
#
# [168] Excel Sheet Column Title
#
# https://leetcode.com/problems/excel-sheet-column-title/description/
#
# algorithms
# Easy (47.2%)
# Likes:    6115
# Dislikes: 927
# Total Accepted:    780K
# Total Submissions: 1.7M
# Testcase Example:  "1"
#
# Given an integer columnNumber, return its corresponding column title as it
# appears in an Excel sheet.
#
# For example:
#
# A -> 1
# B -> 2
# C -> 3
# ...
# Z -> 26
# AA -> 27
# AB -> 28
# ...
#
# Example 1:
#
# Input: columnNumber = 1
# Output: "A"
#
# Example 2:
#
# Input: columnNumber = 28
# Output: "AB"
#
# Example 3:
#
# Input: columnNumber = 701
# Output: "ZY"
#
# Constraints:
#
# 1 <= columnNumber <= 2^31 - 1
#

# @lc code=start
class Solution:
    def convertToTitle(self, columnNumber: int) -> str:
        """
        Interview explanation:
        Excel titles are 1-indexed base-26 (A=1 ... Z=26, AA=27). Convert by
        repeatedly taking remainders after mapping to 0-indexed digits.

        Algorithm:
        - While columnNumber > 0: decrement by 1, append chr(n % 26 + 'A'),
          then n //= 26.
        - Reverse the collected characters.

        Complexity: O(log_26 columnNumber) time and space.
        """
        chars = []
        n = columnNumber
        while n:
            n -= 1
            chars.append(chr(n % 26 + ord("A")))
            n //= 26
        return "".join(reversed(chars))
# @lc code=end
