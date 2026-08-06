#
# @lc app=leetcode id=6 lang=python3
#
# [6] Zigzag Conversion
#
# https://leetcode.com/problems/zigzag-conversion/description/
#
# algorithms
# Medium (54.07%)
# Likes:    9394
# Dislikes: 15944
# Total Accepted:    2.2M
# Total Submissions: 4.1M
# Testcase Example:  '"PAYPALISHIRING"\n3'
#
# The string "PAYPALISHIRING" is written in a zigzag pattern on a given number
# of rows like this: (you may want to display this pattern in a fixed font for
# better legibility)
# 
# 
# P   A   H   N
# A P L S I I G
# Y   I   R
# 
# 
# And then read line by line: "PAHNAPLSIIGYIR"
# 
# Write the code that will take a string and make this conversion given a
# number of rows:
# 
# 
# string convert(string s, int numRows);
# 
# 
# 
# Example 1:
# 
# 
# Input: s = "PAYPALISHIRING", numRows = 3
# Output: "PAHNAPLSIIGYIR"
# 
# 
# Example 2:
# 
# 
# Input: s = "PAYPALISHIRING", numRows = 4
# Output: "PINALSIGYAHRPI"
# Explanation:
# P     I    N
# A   L S  I G
# Y A   H R
# P     I
# 
# 
# Example 3:
# 
# 
# Input: s = "A", numRows = 1
# Output: "A"
# 
# 
# 
# Constraints:
# 
# 
# 1 <= s.length <= 1000
# s consists of English letters (lower-case and upper-case), ',' and '.'.
# 1 <= numRows <= 1000
# 
# 
#

# @lc code=start
from typing import List, Optional
class Solution:
    def convert(self, s: str, numRows: int) -> str:
        """
        Interview explanation:
        The zigzag layout only matters by row order, not by the visual columns.
        Keep one list of characters per row and simulate the vertical/downward
        then diagonal/upward movement. Lists are chosen because appending chars
        is O(1), and one final join avoids quadratic string concatenation.

        Algorithm:
        - If numRows is 1, no zigzag is possible.
        - Move current_row by direction (+1 or -1).
        - Reverse direction at the first and last row.
        - Join rows in order.

        Edge cases and tests:
        - numRows == 1 returns the original string.
        - numRows >= len(s) also naturally returns the original order.
        - Standard examples: PAYPALISHIRING with 3 or 4 rows.

        Complexity: O(n) time and O(n) space for the row buffers.
        """
        if numRows == 1 or numRows >= len(s):
            return s

        rows = [[] for _ in range(numRows)]
        row = 0
        step = 1

        for ch in s:
            rows[row].append(ch)
            if row == 0:
                step = 1
            elif row == numRows - 1:
                step = -1
            row += step

        return ''.join(''.join(r) for r in rows)
# @lc code=end


