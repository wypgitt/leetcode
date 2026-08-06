#
# @lc app=leetcode id=171 lang=python3
#
# [171] Excel Sheet Column Number
#
# https://leetcode.com/problems/excel-sheet-column-number/description/
#
# algorithms
# Easy (68.21%)
# Likes:    5133
# Dislikes: 403
# Total Accepted:    940K
# Total Submissions: 1.4M
# Testcase Example:  "\"A\""
#
# Given a string columnTitle that represents the column title as appears in an
# Excel sheet, return its corresponding column number.
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
# Input: columnTitle = "A"
# Output: 1
#
# Example 2:
#
# Input: columnTitle = "AB"
# Output: 28
#
# Example 3:
#
# Input: columnTitle = "ZY"
# Output: 701
#
# Constraints:
#
# 1 <= columnTitle.length <= 7
#
# columnTitle consists only of uppercase English letters.
#
# columnTitle is in the range ["A", "FXSHRXW"].
#

# @lc code=start
class Solution:
    def titleToNumber(self, columnTitle: str) -> int:
        """
        Interview explanation:
        Interpret the title as a 1-indexed base-26 integer (A=1 ... Z=26).

        Algorithm:
        - result = 0; for each char: result = result * 26 + (ord(c) - 'A' + 1).

        Complexity: O(L) time, O(1) space.
        """
        result = 0
        for ch in columnTitle:
            result = result * 26 + (ord(ch) - ord("A") + 1)
        return result
# @lc code=end
