#
# @lc app=leetcode id=2194 lang=python3
#
# [2194] Cells in a Range on an Excel Sheet
#
# https://leetcode.com/problems/cells-in-a-range-on-an-excel-sheet/description/
#
# algorithms
# Easy (84.09%)
# Likes:    655
# Dislikes: 100
# Total Accepted:    88.4K
# Total Submissions: 105.2K
# Testcase Example:  "\"K1:L2\""
#
# A cell (r, c) of an excel sheet is represented as a string "<col><row>" where:
#
#
# <col> denotes the column number c of the cell. It is represented by
# alphabetical letters.
#
#
#
#
# For example, the 1^st column is denoted by 'A', the 2^nd by 'B', the 3^rd by
# 'C', and so on.
#
#
#
#
#
#
# <row> is the row number r of the cell. The r^th row is represented by the
# integer r.
#
# You are given a string s in the format "<col1><row1>:<col2><row2>", where
# <col1> represents the column c1, <row1> represents the row r1, <col2>
# represents the column c2, and <row2> represents the row r2, such that r1 <= r2
# and c1 <= c2.
#
# Return the list of cells (x, y) such that r1 <= x <= r2 and c1 <= y <= c2. The
# cells should be represented as strings in the format mentioned above and be
# sorted in non-decreasing order first by columns and then by rows.
#
#
#
# Example 1:
#
# Input: s = "K1:L2"
# Output: ["K1","K2","L1","L2"]
# Explanation:
# The above diagram shows the cells which should be present in the list.
# The red arrows denote the order in which the cells should be presented.
#
# Example 2:
#
# Input: s = "A1:F1"
# Output: ["A1","B1","C1","D1","E1","F1"]
# Explanation:
# The above diagram shows the cells which should be present in the list.
# The red arrow denotes the order in which the cells should be presented.
#
#
#
# Constraints:
#
#
# s.length == 5
#
#
# 'A' <= s[0] <= s[3] <= 'Z'
#
#
# '1' <= s[1] <= s[4] <= '9'
#
#
# s consists of uppercase English letters, digits and ':'.
#

# @lc code=start
from typing import List


class Solution:
    def cellsInRange(self, s: str) -> List[str]:
        """
        Interview explanation:
        s like "A1:F1" — return all cells in the rectangle col1..col2, row1..row2
        in row-major / column-major order: columns outer, rows inner as specified
        (col from c1 to c2, for each col row from r1 to r2).

        Algorithm:
        - Parse c1,r1,c2,r2; nested loops.

        Complexity: O((c2-c1)*(r2-r1)) time/space.
        """
        c1, r1, _, c2, r2 = s[0], s[1], s[2], s[3], s[4]
        ans = []
        for c in range(ord(c1), ord(c2) + 1):
            for r in range(ord(r1), ord(r2) + 1):
                ans.append(chr(c) + chr(r))
        return ans
# @lc code=end
