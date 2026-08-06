#
# @lc app=leetcode id=2617 lang=python3
#
# [2617] Minimum Number of Visited Cells in a Grid
#

# --- Notes (problem, modeling, backward DP, segment tree, merge rule, complexity, edges, interview) ---
#
# Problem restatement
# m x n grid `grid`. Start at (0, 0). From (i, j) you may move to:
#   - (i, k) for any integer k with j < k <= j + grid[i][j]   (same row, jump right),
#   - (k, j) for any integer k with i < k <= i + grid[i][j]   (same column, jump down).
# Each move lands on a new cell; count VISITED cells along the path (the starting cell counts).
# Return the minimum possible visited-cell count to reach (m-1, n-1), or -1 if unreachable.
#
# Modeling
# Directed graph on cells (each jump is an edge). Edge weights are uniform if we count “extra”
# cells per jump — minimizing visited cells from start to goal equals shortest path where each
# edge from (i,j) to a farther cell costs +1 visited cell for the new cell (prefix length grows by 1).
# Naive BFS / Dijkstra explores O(outdegree) per cell and can be too heavy when jumps are long.
#
# Backward DP (reverse relaxation)
# Let f(i, j) = minimum number of visited cells needed to finish at (m-1, n-1) when we START the
# remaining journey at (i, j), counting (i, j) itself. Then f(m-1, n-1) = 1 (only that cell).
# From (i, j), the next step either jumps right to (i, k) with k > j or down to (k, j) with k > i,
# inside the grid and within grid[i][j] reach. Equivalently, reading backward:
#   f(i, j) = 1 + min( min_{k in reachable right range} f(i, k), min_{k in reachable down range} f(k, j) ),
# where reachable ranges are exactly those imposed by forward jumps from (i, j).
# Process cells in decreasing i and j so that when computing f(i, j), all f on strictly larger
# row index (same column) or larger column index (same row) are already known — exactly like a
# DAG relaxation from bottom-right to top-left.
#
# Range-min queries
# For fixed row i, we need min f(i, k) for k in [j+1, min(n-1, j + grid[i][j])].
# For fixed column j, we need min f(k, j) for k in [i+1, min(m-1, i + grid[i][j])].
# A segment tree per row (length n) and per column (length m) supports point update and range
# minimum in O(log n) / O(log m).
#
# Critical implementation detail — do not overwrite the goal cell with “infinity”
# When both forward ranges are empty (already at last column / row), min queries return INF.
# The formula “min(mr, md) + 1” would incorrectly inflate INF. Also the bottom-right cell is
# initialized to 1 before the sweep; we must combine with the existing stored value:
#   cur = min(row.query(j,j), col.query(i,i))
#   if both range mins are INF: new_val = cur
#   else: new_val = min(cur, min(mr, md) + 1)
# Grid cells with grid[i][j] == 0 cannot jump; skip updates (destination may still hold its init).
#
# Time complexity
# O(m n (log n + log m)) for m*n cells each doing O(log n + log m) segment-tree work.
#
# Space complexity
# O(m n) for segment-tree storage (m trees of size O(n) + n trees of size O(m), linear total memory).
#
# Edge cases
# - m = n = 1: answer 1.
# - grid[i][j] = 0: cannot leave that cell by jumping (unless already at goal with value set).
# - Unreachable goal: row0/col0 query at (0,0) stays INF -> return -1.
#
# Improvements / alternatives
# - Monotone stacks / deques per row/column can sometimes shave logs for special structures.
# - Forward multi-source BFS with pruning — same asymptotics often worse constant factors.
#
# LeetCode submission
# Imports inside the LC code section markers (typing.List).
#
# Interview walkthrough
# 1) Observe DAG order by increasing (i+j) or decreasing sweep from target.
# 2) Write recurrence; reduce to range-min on rows and columns.
# 3) Segment trees (or heaps with lazy cleanup) for dynamic mins.
# 4) Handle INF arithmetic and the fixed goal cell carefully.
# --- end notes ---

# @lc code=start
from typing import List


class _SegTree:
    """Iterative range-min segment tree with point assignment."""

    __slots__ = ("inf", "size", "t")

    def __init__(self, n: int, inf: int) -> None:
        """
        Interview explanation:
        Build an iterative range-min segment tree over n positions, filled with inf.

        Algorithm:
        - Round size up to a power of two; allocate 2*size leaves/internal nodes.

        Complexity: O(n) time and space.
        """
        self.inf = inf
        self.size = 1
        while self.size < n:
            self.size <<= 1
        self.t = [inf] * (2 * self.size)

    def _pull(self, i: int) -> None:
        self.t[i] = min(self.t[i << 1], self.t[i << 1 | 1])

    def update(self, pos: int, val: int) -> None:
        i = pos + self.size
        self.t[i] = val
        i >>= 1
        while i:
            self._pull(i)
            i >>= 1

    def query(self, l: int, r: int) -> int:
        if l > r:
            return self.inf
        l += self.size
        r += self.size
        res = self.inf
        while l <= r:
            if l & 1:
                res = min(res, self.t[l])
                l += 1
            if not (r & 1):
                res = min(res, self.t[r])
                r -= 1
            l >>= 1
            r >>= 1
        return res


class Solution:
    def minimumVisitedCells(self, grid: List[List[int]]) -> int:
        """
        Interview explanation:
        From (0,0) jump right/down within grid[i][j]; return the minimum number of
        visited cells to reach (m-1, n-1), or -1 if unreachable.

        Algorithm:
        - Backward DP: f(i,j) = 1 + min over reachable right/down cells of f(next).
        - Sweep cells from bottom-right to top-left; maintain a range-min segment tree
          per row and per column for point update / range query.
        - Goal cell starts at 1; carefully combine with INF when ranges are empty.

        Complexity: O(mn(log n + log m)) time, O(mn) space.
        """
        m, n = len(grid), len(grid[0])
        INF = 10**9

        rows = [_SegTree(n, INF) for _ in range(m)]
        cols = [_SegTree(m, INF) for _ in range(n)]

        rows[m - 1].update(n - 1, 1)
        cols[n - 1].update(m - 1, 1)

        for i in range(m - 1, -1, -1):
            for j in range(n - 1, -1, -1):
                if grid[i][j] == 0:
                    continue
                r_max = min(n - 1, j + grid[i][j])
                d_max = min(m - 1, i + grid[i][j])
                mr = rows[i].query(j + 1, r_max)
                md = cols[j].query(i + 1, d_max)
                cur = min(rows[i].query(j, j), cols[j].query(i, i))
                if mr >= INF and md >= INF:
                    new_val = cur
                else:
                    new_val = min(cur, min(mr, md) + 1)
                rows[i].update(j, new_val)
                cols[j].update(i, new_val)

        res = rows[0].query(0, 0)
        return -1 if res >= INF else res


# @lc code=end
