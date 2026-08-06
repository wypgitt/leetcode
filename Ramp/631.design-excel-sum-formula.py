#
# @lc app=leetcode id=631 lang=python3
#
# [631] Design Excel Sum Formula
#
# https://leetcode.com/problems/design-excel-sum-formula/description/
#
# algorithms
# Hard (39.50%)
# Likes:    285
# Dislikes: 298
# Total Accepted:    36.5K
# Total Submissions: 92.4K
# Testcase Example:  "[\"Excel\",\"set\",\"sum\",\"set\",\"get\"]\n[[3,\"C\"],[1,\"A\",2],[3,\"C\",[\"A1\",\"A1:B2\"]],[2,\"B\",2],[3,\"C\"]]"
#
#
# Design the basic function of Excel and implement the function of the sum
# formula.
#
# Implement the Excel class:
#
# Excel(int height, char width) Initializes the object with the height and
# the width of the sheet. The sheet is an integer matrix mat of size
# height x width with the row index in the range [1, height] and the
# column index in the range ['A', width]. All the values should be zero
# initially.
#
# void set(int row, char column, int val) Changes the value at
# mat[row][column] to be val.
#
# int get(int row, char column) Returns the value at mat[row][column].
#
# int sum(int row, char column, List<String> numbers) Sets the value at
# mat[row][column] to be the sum of cells represented by numbers and
# returns the value at mat[row][column]. This sum formula should exist
# until this cell is overlapped by another value or another sum formula.
# numbers[i] could be on the format:
#
# "ColRow" that represents a single cell.
#
# For example, "F7" represents the cell mat[7]['F'].
#
# "ColRow1:ColRow2" that represents a range of cells. The range will
# always be a rectangle where "ColRow1" represent the position of the
# top-left cell, and "ColRow2" represents the position of the bottom-right
# cell.
#
# For example, "B3:F7" represents the cells mat[i][j] for 3 <= i <= 7 and
# 'B' <= j <= 'F'.
#
# Note: You could assume that there will not be any circular sum
# reference.
#
# For example, mat[1]['A'] == sum(1, "B") and mat[1]['B'] == sum(1, "A").
#
# Example 1:
#
# Input
# ["Excel", "set", "sum", "set", "get"]
# [[3, "C"], [1, "A", 2], [3, "C", ["A1", "A1:B2"]], [2, "B", 2], [3,
# "C"]]
# Output
# [null, null, 4, null, 6]
#
# Explanation
# Excel excel = new Excel(3, "C");
#  // construct a 3*3 2D array with all zero.
#  //   A B C
#  // 1 0 0 0
#  // 2 0 0 0
#  // 3 0 0 0
# excel.set(1, "A", 2);
#  // set mat[1]["A"] to be 2.
#  //   A B C
#  // 1 2 0 0
#  // 2 0 0 0
#  // 3 0 0 0
# excel.sum(3, "C", ["A1", "A1:B2"]); // return 4
#  // set mat[3]["C"] to be the sum of value at mat[1]["A"] and the values
# sum of the rectangle range whose top-left cell is mat[1]["A"] and
# bottom-right cell is mat[2]["B"].
#  //   A B C
#  // 1 2 0 0
#  // 2 0 0 0
#  // 3 0 0 4
# excel.set(2, "B", 2);
#  // set mat[2]["B"] to be 2. Note mat[3]["C"] should also be changed.
#  //   A B C
#  // 1 2 0 0
#  // 2 0 2 0
#  // 3 0 0 6
# excel.get(3, "C"); // return 6
#
# Constraints:
#
# 1 <= height <= 26
#
# 'A' <= width <= 'Z'
#
# 1 <= row <= height
#
# 'A' <= column <= width
#
# -100 <= val <= 100
#
# 1 <= numbers.length <= 5
#
# numbers[i] has the format "ColRow" or "ColRow1:ColRow2".
#
# At most 100 calls will be made to set, get, and sum.
#
# @lc code=start

from typing import List


class Excel:
    def __init__(self, height: int, width: str):
        """
        Interview explanation:
        Premium. Spreadsheet with set/get and sum formulas over cell ranges.
        Formulas are stored as dependency lists; get recursively evaluates.

        Algorithm:
        - Grid of height rows x (ord(width)-'A'+1) cols.
        - formulas[r][c] = dict of cell -> multiplicity for SUM, or None if raw.

        Complexity: O(H*W) space.
        """
        self.h = height
        self.w = ord(width) - ord("A") + 1
        self.vals = [[0] * self.w for _ in range(self.h)]
        self.formulas = [[None] * self.w for _ in range(self.h)]

    def _parse(self, cell: str):
        col = ord(cell[0]) - ord("A")
        row = int(cell[1:]) - 1
        return row, col

    def _expand(self, numbers: List[str]):
        from collections import Counter

        cnt = Counter()
        for token in numbers:
            if ":" in token:
                a, b = token.split(":")
                r1, c1 = self._parse(a)
                r2, c2 = self._parse(b)
                for r in range(min(r1, r2), max(r1, r2) + 1):
                    for c in range(min(c1, c2), max(c1, c2) + 1):
                        cnt[(r, c)] += 1
            else:
                cnt[self._parse(token)] += 1
        return cnt

    def set(self, row: int, column: str, val: int) -> None:
        """
        Interview explanation:
        Set a cell to a raw integer, clearing any sum formula.

        Algorithm:
        - formulas[row-1][col] = None; vals[...] = val.

        Complexity: O(1).
        """
        r, c = row - 1, ord(column) - ord("A")
        self.formulas[r][c] = None
        self.vals[r][c] = val

    def get(self, row: int, column: str) -> int:
        """
        Interview explanation:
        Return cell value; if it has a SUM formula, recursively sum dependencies.

        Algorithm:
        - If no formula return vals.
        - Else sum multiplicity * get(dep) for each dependency.

        Complexity: O(D) over dependency graph size (no cycles by problem).
        """
        r, c = row - 1, ord(column) - ord("A")
        f = self.formulas[r][c]
        if f is None:
            return self.vals[r][c]
        total = 0
        for (rr, cc), m in f.items():
            total += m * self.get(rr + 1, chr(ord("A") + cc))
        return total

    def sum(self, row: int, column: str, numbers: List[str]) -> int:
        """
        Interview explanation:
        Set cell to SUM of ranges/cells in numbers; return computed value.

        Algorithm:
        - Expand tokens ("A1", "A1:B2") into multiset of cells.
        - Store as formula; return get(row, column).

        Complexity: O(cells in ranges) to expand; get as above.
        """
        r, c = row - 1, ord(column) - ord("A")
        self.formulas[r][c] = self._expand(numbers)
        return self.get(row, column)


# Your Excel object will be instantiated and called as such:
# obj = Excel(height, width)
# obj.set(row, column, val)
# param_2 = obj.get(row, column)
# param_3 = obj.sum(row, column, numbers)
# @lc code=end
