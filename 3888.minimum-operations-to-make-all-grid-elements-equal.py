#
# @lc app=leetcode id=3888 lang=python3
#
# [3888] Minimum Operations to Make All Grid Elements Equal
#
# --- Notes (problem restatement, greedy scan, 2D difference, targets mx/mx+1, complexity) ---
#
# Problem restatement
# m x n grid grid, integer k in [1, min(m,n)]. One operation: choose ANY k x k submatrix
# (contiguous rows and columns) and add 1 to every cell inside it.
# Minimum number of operations so all cells become EQUAL. Only increments are allowed, so
# the final common value T must satisfy T >= max(grid). If impossible, return -1.
#
# Greedy order (why scan row-major from top-left)
# Operations only increase values. Fix a target T. While scanning (i, j) in increasing
# row-major order, the current augmented value cur(i,j) equals grid[i][j] plus all
# increments from operations whose k x k blocks already chosen affect this cell.
# Any operation whose k x k window has top-left at (r, c) with r > i or (r == i and c > j)
# has NOT been decided yet when we stand at (i, j), so it cannot help raise (i, j).
# Therefore if cur(i,j) < T, the ONLY way to fix it using future-valid choices is to add
# operations with top-left exactly at (i, j) (1-based indexing in the editorial loop).
# If cur(i,j) < T but the k x k square starting at (i, j) does not fit inside the grid,
# the cell can never catch up -> infeasible for this T.
# If cur(i,j) > T, overshoot cannot be fixed with only increases -> infeasible.
#
# Counting operations at (i, j)
# If cur < T, need = T - cur; we perform need operations each adding a full k x k stamp with
# top-left at (i, j). Total operations accumulate += need.
#
# 2D difference array (why not naive k^2 updates)
# Naively touching k^2 cells per stamp yields O(m n k^2). Instead maintain a 2D difference
# D such that the PREFIX sum at (i,j) equals total increment added to grid cell (i,j).
# Adding `need` to the rectangle [i..i+k-1] x [j..j+k-1] in 1-based coordinates uses the
# classic four-corner update on D:
#   D[i][j]       += need
#   D[i+k][j]     -= need
#   D[i][j+k]     -= need
#   D[i+k][j+k]   += need
# Then recover the increment at (i,j) by inclusive prefix accumulation:
#   acc[i][j] = D[i][j] + acc[i-1][j] + acc[i][j-1] - acc[i-1][j-1]
# The implementation folds acc into the same `diff` grid: each step first applies the
# prefix formula to obtain cur_val, then possibly applies corner updates for new stamps.
#
# Which target T?
# Always T >= mx = max(grid). Usually T = mx works (minimum possible final value). Overlap
# of stamps can force some cells to receive extra passive increments; occasionally the
# naive minimum mx is too low under greedy feasibility. It suffices to try only T = mx and
# T = mx + 1; if both checks fail, no integer T works -> return -1 (editorial claim).
#
# check(T) returns
# - total operation count if greedy achieves exactly flat T everywhere;
# - -1 if infeasible (overshoot, cannot fit stamp, etc.).
#
# Time complexity
# O(m * n) per target, two targets -> O(m * n). Each cell O(1) arithmetic.
#
# Space complexity
# O(m * n) for the padded difference/prefix grid (size (m+2) x (n+2) for safe indices).
#
# Edge cases
# - k == 1: operation is single-cell increment; greedy reduces to each cell needing
#   max(0, T - grid[i][j]) ops — consistent with Example 2 (sum of deficits to T = max).
# - All cells already equal and k fits: often zero ops at T = mx.
# - Large coordinates: use Python int; padded arrays avoid boundary checks on difference.
#
# Possible improvements
# - Single pass could exit early on first failure; structure kept clear with check().
# - If constraints guaranteed mx works whenever possible, second check might be skipped in
#   theory — problem statement uses two tries for safety.
#
# Interview walkthrough
# 1) Only increases -> common value T >= max entry.
# 2) Row-major greedy: first moment to fix cell (i,j) is stamp top-left (i,j).
# 3) 2D difference for O(1) rectangle adds + O(1) cell query via running 2D prefix.
# 4) Try T = max and max+1; else impossible.
# --- end notes ---

# @lc code=start
class Solution:
    def minOperations(self, grid: list[list[int]], k: int) -> int:
        m, n = len(grid), len(grid[0])
        mx = max(max(row) for row in grid)

        def check(target: int) -> int:
            diff = [[0] * (n + 2) for _ in range(m + 2)]
            total_ops = 0

            for i, row in enumerate(grid, 1):
                for j, val in enumerate(row, 1):
                    diff[i][j] += (
                        diff[i - 1][j] + diff[i][j - 1] - diff[i - 1][j - 1]
                    )

                    cur_val = val + diff[i][j]

                    if cur_val > target:
                        return -1

                    if cur_val < target:
                        if i + k - 1 > m or j + k - 1 > n:
                            return -1

                        needed = target - cur_val
                        total_ops += needed
                        diff[i][j] += needed
                        diff[i + k][j] -= needed
                        diff[i][j + k] -= needed
                        diff[i + k][j + k] += needed

            return total_ops

        for t in range(mx, mx + 2):
            res = check(t)
            if res != -1:
                return res

        return -1


# @lc code=end
