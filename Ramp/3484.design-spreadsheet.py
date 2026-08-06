#
# @lc app=leetcode id=3484 lang=python3
#
# [3484] Design Spreadsheet
#
# https://leetcode.com/problems/design-spreadsheet/description/
#
# algorithms
# Medium (73.85%)
# Likes:    334
# Dislikes: 31
# Total Accepted:    123.5K
# Total Submissions: 167.3K
# Testcase Example:  "[\"Spreadsheet\",\"getValue\",\"setCell\",\"getValue\",\"setCell\",\"getValue\",\"resetCell\",\"getValue\"]\n[[3],[\"=5+7\"],[\"A1\",10],[\"=A1+6\"],[\"B2\",15],[\"=A1+B2\"],[\"A1\"],[\"=A1+B2\"]]"
#
#
# A spreadsheet is a grid with 26 columns (labeled from 'A' to 'Z') and a
# given number of rows. Each cell in the spreadsheet can hold an integer
# value between 0 and 10^5.
#
# Implement the Spreadsheet class:
#
# Spreadsheet(int rows) Initializes a spreadsheet with 26 columns (labeled
# 'A' to 'Z') and the specified number of rows. All cells are initially
# set to 0.
#
# void setCell(String cell, int value) Sets the value of the specified
# cell. The cell reference is provided in the format "AX" (e.g., "A1",
# "B10"), where the letter represents the column (from 'A' to 'Z') and the
# number represents a 1-indexed row.
#
# void resetCell(String cell) Resets the specified cell to 0.
#
# int getValue(String formula) Evaluates a formula of the form "=X+Y",
# where X and Y are either cell references or non-negative integers, and
# returns the computed sum.
#
# Note: If getValue references a cell that has not been explicitly set
# using setCell, its value is considered 0.
#
# Example 1:
#
# Input:
#
# ["Spreadsheet", "getValue", "setCell", "getValue", "setCell",
# "getValue", "resetCell", "getValue"]
#
# [[3], ["=5+7"], ["A1", 10], ["=A1+6"], ["B2", 15], ["=A1+B2"], ["A1"],
# ["=A1+B2"]]
#
# Output:
#
# [null, 12, null, 16, null, 25, null, 15]
#
# Explanation
#
# Spreadsheet spreadsheet = new Spreadsheet(3); // Initializes a
# spreadsheet with 3 rows and 26 columns
#
# spreadsheet.getValue("=5+7"); // returns 12 (5+7)
#
# spreadsheet.setCell("A1", 10); // sets A1 to 10
#
# spreadsheet.getValue("=A1+6"); // returns 16 (10+6)
#
# spreadsheet.setCell("B2", 15); // sets B2 to 15
#
# spreadsheet.getValue("=A1+B2"); // returns 25 (10+15)
#
# spreadsheet.resetCell("A1"); // resets A1 to 0
#
# spreadsheet.getValue("=A1+B2"); // returns 15 (0+15)
#
# Constraints:
#
# 1 <= rows <= 10^3
#
# 0 <= value <= 10^5
#
# The formula is always in the format "=X+Y", where X and Y are either
# valid cell references or non-negative integers with values less than or
# equal to 10^5.
#
# Each cell reference consists of a capital letter from 'A' to 'Z'
# followed by a row number between 1 and rows.
#
# At most 10^4 calls will be made in total to setCell, resetCell, and
# getValue.
#

# @lc code=start
class Spreadsheet:
    """
    Interview explanation:
    26-column grid; cells default to 0. Formulas are always "=X+Y" where each
    operand is a cell ref or integer.

    Algorithm:
    - Sparse cell -> value map (unset = 0).
    - Parse operands: digit start → int, else look up cell.
    """

    def __init__(self, rows: int):
        """
        Interview explanation:
        Initialize empty spreadsheet (rows unused beyond validation by caller).

        Algorithm:
        - Sparse dict of cell values.

        Complexity: O(1) time, O(1) space initially.
        """
        self.cells = {}

    def setCell(self, cell: str, value: int) -> None:
        """
        Interview explanation:
        Set a cell to an explicit integer value.

        Algorithm:
        - cells[cell] = value.

        Complexity: O(1) time, O(1) space.
        """
        self.cells[cell] = value

    def resetCell(self, cell: str) -> None:
        """
        Interview explanation:
        Reset a cell to 0 (equivalent to deleting the sparse entry).

        Algorithm:
        - Pop cell from map.

        Complexity: O(1) time, O(1) space.
        """
        self.cells.pop(cell, None)

    def getValue(self, formula: str) -> int:
        """
        Interview explanation:
        Evaluate "=X+Y" where X,Y are cell refs or non-negative integers.

        Algorithm:
        - Split on '+'; resolve each operand via _val.

        Complexity: O(1) time, O(1) space.
        """
        x, y = formula[1:].split('+')
        return self._val(x) + self._val(y)

    def _val(self, token: str) -> int:
        if token[0].isdigit():
            return int(token)
        return self.cells.get(token, 0)


# Your Spreadsheet object will be instantiated and called as such:
# obj = Spreadsheet(rows)
# obj.setCell(cell,value)
# obj.resetCell(cell)
# param_3 = obj.getValue(formula)
# @lc code=end
