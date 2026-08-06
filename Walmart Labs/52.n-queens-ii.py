#
# @lc app=leetcode id=52 lang=python3
#
# [52] N-Queens II
#
# https://leetcode.com/problems/n-queens-ii/description/
#
# algorithms
# Hard (79.13%)
# Likes:    4339
# Dislikes: 283
# Total Accepted:    637K
# Total Submissions: 805K
# Testcase Example:  "4"
#
# The n-queens puzzle is the problem of placing n queens on an n x n chessboard
# such that no two queens attack each other.
#
# Given an integer n, return the number of distinct solutions to the n-queens
# puzzle.
#
# Example 1:
#
# Input: n = 4
# Output: 2
# Explanation: There are two distinct solutions to the 4-queens puzzle as
# shown.
#
# Example 2:
#
# Input: n = 1
# Output: 1
#
# Constraints:
#
# 1 <= n <= 9
#

# @lc code=start
class Solution:
    def totalNQueens(self, n: int) -> int:
        """
        Interview explanation:
        Count N-Queens solutions with bitsets: columns, diagonals, and
        anti-diagonals packed into integers. Available slots are free bits in
        the current row mask.

        Algorithm:
        - bits = ~(cols | diag | anti) & ((1 << n) - 1) are free columns.
        - Pick lowest set bit repeatedly; recurse with updated masks.
        - Increment answer when row == n.

        Complexity: O(n!) time, O(n) recursion space.
        """
        return self.totalNQueens_bitset(n)

    def totalNQueens_bitset(self, n: int) -> int:
        """
        Interview explanation:
        Bitmask backtracking (same as primary).

        Algorithm:
        - Place queens using column/diagonal bit masks.

        Complexity: O(n!) time, O(n) space.
        """
        full = (1 << n) - 1
        count = 0

        def dfs(cols: int, diag: int, anti: int) -> None:
            nonlocal count
            if cols == full:
                count += 1
                return
            available = ~(cols | diag | anti) & full
            while available:
                bit = available & -available
                available -= bit
                dfs(cols | bit, (diag | bit) << 1, (anti | bit) >> 1)

        dfs(0, 0, 0)
        return count

    def totalNQueens_sets(self, n: int) -> int:
        """
        Interview explanation:
        Same search as N-Queens I, counting boards instead of materializing
        them; uses hash sets for columns and diagonals.

        Algorithm:
        - Backtrack by row; skip occupied cols / diags.

        Complexity: O(n!) time, O(n) space.
        """
        cols: set[int] = set()
        diag: set[int] = set()
        anti: set[int] = set()
        count = 0

        def backtrack(row: int) -> None:
            nonlocal count
            if row == n:
                count += 1
                return
            for col in range(n):
                if col in cols or (row - col) in diag or (row + col) in anti:
                    continue
                cols.add(col)
                diag.add(row - col)
                anti.add(row + col)
                backtrack(row + 1)
                cols.remove(col)
                diag.remove(row - col)
                anti.remove(row + col)

        backtrack(0)
        return count
# @lc code=end
