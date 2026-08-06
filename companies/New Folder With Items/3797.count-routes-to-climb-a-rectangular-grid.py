#
# @lc app=leetcode id=3797 lang=python3
#
# [3797] Count Routes to Climb a Rectangular Grid
#
# https://leetcode.com/problems/count-routes-to-climb-a-rectangular-grid/description/
#
# algorithms
# Hard (24.64%)
# Likes:    42
# Dislikes: 1
# Total Accepted:    3.8K
# Total Submissions: 15.3K
# Testcase Example:  '["..","#."]\n1'
#
# You are given a string array grid of size n, where each string grid[i] has
# length m. The character grid[i][j] is one of the following symbols:
# 
# 
# '.': The cell is available.
# '#': The cell is blocked.
# 
# 
# You want to count the number of different routes to climb grid. Each route
# must start from any cell in the bottom row (row n - 1) and end in the top row
# (row 0).
# 
# However, there are some constraints on the route.
# 
# 
# You can only move from one available cell to another available cell.
# The Euclidean distance of each move is at most d, where d is an integer
# parameter given to you. The Euclidean distance between two cells (r1, c1),
# (r2, c2) is sqrt((r1 - r2)^2 + (c1 - c2)^2).
# Each move either stays on the same row or moves to the row directly above
# (from row r to r - 1).
# You cannot stay on the same row for two consecutive turns. If you stay on the
# same row in a move (and this move is not the last move), your next move must
# go to the row above.
# 
# 
# Return an integer denoting the number of such routes. Since the answer may be
# very large, return it modulo 10^9 + 7.
# 
# 
# Example 1:
# 
# 
# Input: grid = ["..","#."], d = 1
# 
# Output: 2
# 
# Explanation:
# 
# We label the cells we visit in the routes sequentially, starting from 1. The
# two routes are:
# 
# 
# .2
# #1
# 
# 
# 
# 32
# #1
# 
# 
# We can move from the cell (1, 1) to the cell (0, 1) because the Euclidean
# distance is sqrt((1 - 0)^2 + (1 - 1)^2) = sqrt(1) <= d.
# 
# However, we cannot move from the cell (1, 1) to the cell (0, 0) because the
# Euclidean distance is sqrt((1 - 0)^2 + (1 - 0)^2) = sqrt(2) > d.
# 
# 
# Example 2:
# 
# 
# Input: grid = ["..","#."], d = 2
# 
# Output: 4
# 
# Explanation:
# 
# Two of the routes are given in example 1. The other two routes are:
# 
# 
# 2.
# #1
# 
# 
# 
# 23
# #1
# 
# 
# Note that we can move from (1, 1) to (0, 0) because the Euclidean distance is
# sqrt(2) <= d.
# 
# 
# Example 3:
# 
# 
# Input: grid = ["#"], d = 750
# 
# Output: 0
# 
# Explanation:
# 
# We cannot choose any cell as the starting cell. Therefore, there are no
# routes.
# 
# 
# Example 4:
# 
# 
# Input: grid = [".."], d = 1
# 
# Output: 4
# 
# Explanation:
# 
# The possible routes are:
# 
# 
# .1
# 
# 
# 
# 1.
# 
# 
# 
# 12
# 
# 
# 
# 21
# 
# 
# 
# 
# Constraints:
# 
# 
# 1 <= n == grid.length <= 750
# 1 <= m == grid[i].length <= 750
# grid[i][j] is '.' or '#'.
# 1 <= d <= 750
# 
# 
#

# @lc code=start
from math import isqrt
from typing import List


class Solution:
    def numberOfRoutes(self, grid: List[str], d: int) -> int:
        """
        Interview explanation
        =====================

        Restate the problem
        -------------------
        We have an `n x m` grid.  A route:

        * starts from any available cell in the bottom row
        * ends in any available cell in the top row
        * can move only to available cells
        * can move within the same row or to the row directly above
        * every move must have Euclidean distance at most `d`
        * cannot make two same-row moves in a row

        Return the number of valid routes modulo `10^9 + 7`.

        Key observations
        ----------------
        Moves never go downward.  They either stay in the current row or move to
        the row above.  Therefore we can process rows from bottom to top.

        The "no two same-row moves consecutively" rule has an important effect:
        after a route enters a row, it can do at most one horizontal move in that
        row before it must move upward, unless that horizontal move ends the
        route in the top row.

        So each row has two phases:

        1. Enter the row.
        2. Optionally make one same-row move.

        After phase 2, the route either moves up to the next row or stops if it
        is already in the top row.

        Distance limits
        ---------------
        Same-row move:

            sqrt((r - r)^2 + (c1 - c2)^2) <= d
            abs(c1 - c2) <= d

        So the horizontal column radius is:

            horizontal_radius = d

        Move to the row above:

            sqrt(1^2 + (c1 - c2)^2) <= d
            1 + (c1 - c2)^2 <= d^2
            abs(c1 - c2) <= floor(sqrt(d^2 - 1))

        So the upward column radius is:

            upward_radius = floor(sqrt(d^2 - 1))

        DP meaning
        ----------
        While processing row `r`, let:

            enter[c] = number of ways to be at cell (r, c) immediately after
                       starting there or moving up into it

        At this point the last move is not a same-row move, so a horizontal move
        is allowed.

        From `enter`, compute:

            after_optional_horizontal[c]

        meaning the number of ways to be at `(r, c)` after either:

        * making no same-row move in this row, or
        * making exactly one same-row move in this row

        For an available target column `c`, this is simply the sum of `enter[p]`
        over all columns `p` within distance `d`:

            c - d <= p <= c + d

        Why does this include "no move" correctly?
        The term `p == c` represents staying at the entered cell and making no
        horizontal move.  Terms `p != c` represent one horizontal move from
        `(r, p)` to `(r, c)`.

        Then, if `r` is not the top row, the ways to enter row `r - 1` are:

            next_enter[c] = sum of after_optional_horizontal[p]
                            where abs(p - c) <= upward_radius

        and `(r - 1, c)` must be available.

        Data structure choice
        ---------------------
        We only need arrays of length `m` for the current row:

        * `enter`
        * `after_optional_horizontal`
        * `next_enter`

        To compute many range sums efficiently, we use prefix sums.  A range
        sum over columns `[left, right]` becomes O(1):

            prefix[right + 1] - prefix[left]

        This turns each row into O(m) work instead of O(m * d).

        Algorithm
        ---------
        1. Initialize `enter[c] = 1` for every available bottom-row cell.
           Each one can be chosen as a starting cell.

        2. For each row from bottom to top:
              a. Use a sliding/prefix range sum with radius `d` to compute
                 `after_optional_horizontal`.

              b. If this is the top row, return the sum of
                 `after_optional_horizontal`.

              c. Otherwise, use a second range sum with radius
                 `floor(sqrt(d^2 - 1))` to compute `enter` for the row above.

        Correctness proof
        -----------------
        Lemma 1: `after_optional_horizontal[c]` correctly counts all ways to be
        at `(r, c)` after processing same-row choices for row `r`.
        A route that enters row `r` at column `p` may end this row phase at
        column `c` if and only if `(r, c)` is available and `abs(p - c) <= d`.
        If `p == c`, the route made no same-row move.  If `p != c`, it made
        exactly one same-row move.  Since two consecutive same-row moves are
        forbidden, these are exactly the allowed possibilities within the row.

        Lemma 2: The transition to `next_enter` correctly counts all ways to
        enter row `r - 1`.
        A route can move from `(r, p)` to `(r - 1, c)` exactly when the target is
        available and:

            sqrt(1 + (p - c)^2) <= d

        which is equivalent to `abs(p - c) <= upward_radius`.  Summing
        `after_optional_horizontal[p]` over that valid range counts every route
        that can enter `(r - 1, c)`.

        Lemma 3: When the algorithm reaches the top row, summing
        `after_optional_horizontal` counts exactly all valid complete routes.
        A route is complete as soon as it is in the top row.  It may either stop
        immediately after entering the top row or make one final same-row move
        and then stop.  Lemma 1 counts exactly those possibilities.

        Theorem: The algorithm returns the number of valid routes.
        The initialization counts all valid starting choices in the bottom row.
        By Lemma 1 and Lemma 2, each row transition preserves exactly the set of
        valid partial routes.  By Lemma 3, the final sum on the top row counts
        exactly all complete routes.

        Complexity analysis
        -------------------
        Let:

            n = number of rows
            m = number of columns

        For each row, we compute a constant number of prefix arrays and scan all
        `m` columns.

        Time:

            O(n * m)

        Space:

            O(m)

        excluding the input grid.

        Edge cases
        ----------
        * No available bottom cell:
          Initialization is all zero, so the answer is zero.

        * No available top cell:
          The top-row sum is zero.

        * Single-row grid:
          The bottom row is also the top row.  We count routes that start and
          stop immediately, plus routes that make one valid same-row move.

        * d = 1:
          Upward moves can only stay in the same column because
          `floor(sqrt(1^2 - 1)) = 0`.

        * Blocked cells:
          We zero out target cells that are blocked in both horizontal and
          upward transitions.

        Test strategy
        -------------
        Useful tests:

        * Provided examples:
              ["..", "#."], d = 1 -> 2
              ["..", "#."], d = 2 -> 4
              ["#"],        d = 750 -> 0
              [".."],       d = 1 -> 4

        * Single available cell.
        * Fully blocked top or bottom row.
        * Small grids compared with brute-force DFS enumeration.

        Possible improvement
        --------------------
        O(n * m) is already optimal up to constant factors because the input
        itself has `n * m` cells.  The key improvement over a direct simulation
        is replacing all radius scans with prefix-sum range queries.
        """

        modulo = 10**9 + 7
        row_count = len(grid)
        col_count = len(grid[0])
        horizontal_radius = d
        upward_radius = isqrt(d * d - 1)

        def range_sums(values: List[int], radius: int, row: str) -> List[int]:
            prefix = [0] * (col_count + 1)
            for col, value in enumerate(values):
                prefix[col + 1] = (prefix[col] + value) % modulo

            result = [0] * col_count
            for col, cell in enumerate(row):
                if cell == '#':
                    continue

                left = max(0, col - radius)
                right = min(col_count - 1, col + radius)
                result[col] = (prefix[right + 1] - prefix[left]) % modulo

            return result

        enter = [1 if cell == '.' else 0 for cell in grid[-1]]

        for row in range(row_count - 1, -1, -1):
            after_optional_horizontal = range_sums(
                enter,
                horizontal_radius,
                grid[row],
            )

            if row == 0:
                return sum(after_optional_horizontal) % modulo

            enter = range_sums(
                after_optional_horizontal,
                upward_radius,
                grid[row - 1],
            )

        return 0
# @lc code=end


if __name__ == "__main__":
    def brute_force_number_of_routes(test_grid: List[str], d: int) -> int:
        rows = len(test_grid)
        cols = len(test_grid[0])
        horizontal_radius = d
        upward_radius = isqrt(d * d - 1)

        def dfs(row: int, col: int, last_move_was_horizontal: bool) -> int:
            if row == 0:
                total = 1
            else:
                total = 0

            if not last_move_was_horizontal:
                for next_col in range(
                    max(0, col - horizontal_radius),
                    min(cols - 1, col + horizontal_radius) + 1,
                ):
                    if next_col != col and test_grid[row][next_col] == '.':
                        total += dfs(row, next_col, True)

            if row > 0:
                for next_col in range(
                    max(0, col - upward_radius),
                    min(cols - 1, col + upward_radius) + 1,
                ):
                    if test_grid[row - 1][next_col] == '.':
                        total += dfs(row - 1, next_col, False)

            return total

        answer = 0
        for col, cell in enumerate(test_grid[-1]):
            if cell == '.':
                answer += dfs(len(test_grid) - 1, col, False)

        return answer % (10**9 + 7)

    solution = Solution()

    fixed_tests = [
        (["..", "#."], 1, 2),
        (["..", "#."], 2, 4),
        (["#"], 750, 0),
        ([".."], 1, 4),
        (["."], 1, 1),
        (["#", "."], 1, 0),
        ([".", "#"], 1, 0),
    ]

    for test_grid, test_d, expected in fixed_tests:
        assert solution.numberOfRoutes(test_grid, test_d) == expected

    brute_force_cases = [
        (["..", ".."], 1),
        (["...", ".#.", "..."], 1),
        (["...", ".#.", "..."], 2),
        ([".#.", "...", "#.."], 2),
        (["...."], 2),
    ]

    for test_grid, test_d in brute_force_cases:
        expected = brute_force_number_of_routes(test_grid, test_d)
        assert solution.numberOfRoutes(test_grid, test_d) == expected
