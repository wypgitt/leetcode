#
# @lc app=leetcode id=1476 lang=python3
#
# [1476] Subrectangle Queries
#
# https://leetcode.com/problems/subrectangle-queries/description/
#
# algorithms
# Medium (86.44%)
# Likes:    674
# Dislikes: 1462
# Total Accepted:    131K
# Total Submissions: 152K
# Testcase Example:  "[\"SubrectangleQueries\",\"getValue\",\"updateSubrectangle\",\"getValue\",\"getValue\",\"updateSubrectangle\",\"getValue\",\"getValue\"]\r"
#
# Implement the class SubrectangleQueries which receives a rows x cols
# rectangle as a matrix of integers in the constructor and supports two
# methods:
#
# 1. updateSubrectangle(int row1, int col1, int row2, int col2, int newValue)
#
# Updates all values with newValue in the subrectangle whose upper left
# coordinate is (row1,col1) and bottom right coordinate is (row2,col2).
#
# 2. getValue(int row, int col)
#
# Returns the current value of the coordinate (row,col) from the rectangle.
#
# Example 1:
#
# Input
# ["SubrectangleQueries","getValue","updateSubrectangle","getValue","getValue","updateSubrectangle","getValue","getValue"]
# [[[[1,2,1],[4,3,4],[3,2,1],[1,1,1]]],[0,2],[0,0,3,2,5],[0,2],[3,1],[3,0,3,2,10],[3,1],[0,2]]
# Output
# [null,1,null,5,5,null,10,5]
# Explanation
# SubrectangleQueries subrectangleQueries = new
# SubrectangleQueries([[1,2,1],[4,3,4],[3,2,1],[1,1,1]]);
# // The initial rectangle (4x3) looks like:
# // 1 2 1
# // 4 3 4
# // 3 2 1
# // 1 1 1
# subrectangleQueries.getValue(0, 2); // return 1
# subrectangleQueries.updateSubrectangle(0, 0, 3, 2, 5);
# // After this update the rectangle looks like:
# // 5 5 5
# // 5 5 5
# // 5 5 5
# // 5 5 5
# subrectangleQueries.getValue(0, 2); // return 5
# subrectangleQueries.getValue(3, 1); // return 5
# subrectangleQueries.updateSubrectangle(3, 0, 3, 2, 10);
# // After this update the rectangle looks like:
# // 5 5 5
# // 5 5 5
# // 5 5 5
# // 10 10 10
# subrectangleQueries.getValue(3, 1); // return 10
# subrectangleQueries.getValue(0, 2); // return 5
#
# Example 2:
#
# Input
# ["SubrectangleQueries","getValue","updateSubrectangle","getValue","getValue","updateSubrectangle","getValue"]
# [[[[1,1,1],[2,2,2],[3,3,3]]],[0,0],[0,0,2,2,100],[0,0],[2,2],[1,1,2,2,20],[2,2]]
# Output
# [null,1,null,100,100,null,20]
# Explanation
# SubrectangleQueries subrectangleQueries = new
# SubrectangleQueries([[1,1,1],[2,2,2],[3,3,3]]);
# subrectangleQueries.getValue(0, 0); // return 1
# subrectangleQueries.updateSubrectangle(0, 0, 2, 2, 100);
# subrectangleQueries.getValue(0, 0); // return 100
# subrectangleQueries.getValue(2, 2); // return 100
# subrectangleQueries.updateSubrectangle(1, 1, 2, 2, 20);
# subrectangleQueries.getValue(2, 2); // return 20
#
# Constraints:
#
# There will be at most 500 operations considering both methods:
# updateSubrectangle and getValue.
#
# 1 <= rows, cols <= 100
#
# rows == rectangle.length
#
# cols == rectangle[i].length
#
# 0 <= row1 <= row2 < rows
#
# 0 <= col1 <= col2 < cols
#
# 1 <= newValue, rectangle[i][j] <= 10^9
#
# 0 <= row < rows
#
# 0 <= col < cols
#

# @lc code=start
from typing import List


class SubrectangleQueries:
    def __init__(self, rectangle: List[List[int]]):
        """
        Interview explanation:
        Matrix with subrectangle updates and point queries. Store matrix and
        apply updates in place (or keep update history for lazy query).

        Algorithm:
        - Deep-copy / keep reference to rectangle grid.

        Complexity: O(1) if keep ref; O(R*C) if copy.
        """
        self.grid = rectangle

    def updateSubrectangle(
        self, row1: int, col1: int, row2: int, col2: int, newValue: int
    ) -> None:
        """
        Interview explanation:
        Set all cells in inclusive subrectangle to newValue.

        Algorithm:
        - Nested loops row1..row2, col1..col2 assign newValue.

        Complexity: O((row2-row1+1)*(col2-col1+1)).
        """
        for r in range(row1, row2 + 1):
            for c in range(col1, col2 + 1):
                self.grid[r][c] = newValue

    def getValue(self, row: int, col: int) -> int:
        """
        Interview explanation:
        Return current value at (row, col).

        Algorithm:
        - return grid[row][col]

        Complexity: O(1).
        """
        return self.grid[row][col]


class SubrectangleQueriesHistory:
    """Alternate: store update list; getValue scans latest covering update."""

    def __init__(self, rectangle: List[List[int]]):
        """
        Interview explanation:
        Alternate design: keep original grid + list of updates; query checks
        latest update covering the cell.

        Algorithm:
        - self.grid = rectangle; self.updates = []

        Complexity: O(1) init.
        """
        self.grid = rectangle
        self.updates = []

    def updateSubrectangle(
        self, row1: int, col1: int, row2: int, col2: int, newValue: int
    ) -> None:
        """
        Interview explanation:
        Record update instead of rewriting cells.

        Algorithm:
        - Append (row1,col1,row2,col2,newValue).

        Complexity: O(1).
        """
        self.updates.append((row1, col1, row2, col2, newValue))

    def getValue(self, row: int, col: int) -> int:
        """
        Interview explanation:
        Scan updates newest-first; else original grid value.

        Algorithm:
        - For update in reversed(updates): if covers (row,col) return value.

        Complexity: O(U) per query.
        """
        for r1, c1, r2, c2, v in reversed(self.updates):
            if r1 <= row <= r2 and c1 <= col <= c2:
                return v
        return self.grid[row][col]


# Your SubrectangleQueries object will be instantiated and called as such:
# obj = SubrectangleQueries(rectangle)
# obj.updateSubrectangle(row1,col1,row2,col2,newValue)
# param_2 = obj.getValue(row,col)
# @lc code=end
