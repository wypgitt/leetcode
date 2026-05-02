#
# @lc app=leetcode id=37 lang=python3
#
# [37] Sudoku Solver
#
# =============================================================================
# INTERVIEW: HOW TO EXPLAIN (elevator → whiteboard)
# =============================================================================
#
# 30 seconds:
#   "Fill empty cells with backtracking: try digits 1–9, recurse to the next
#   cell, undo if we hit a dead end. To check legality fast, I track which
#   digits already appear in each row, column, and 3×3 box with bitmasks."
#
# 2–3 minutes (what interviewers want):
#   - Problem is NP-complete in general, but 9×9 with Sudoku structure is tiny;
#     depth-first search with pruning is standard.
#   - Fixed cell order (here: row-major index 0..80) removes 'which empty cell
#     next?' overhead; any deterministic order works if we undo correctly.
#   - Pruning: before recursing, reject digits that conflict with row/col/box.
#   - State: board plus O(1)-updatable constraints. Bitmasks = compact sets of
#     digits 1–9 as bits 0..8.
#   - Recursion returns bool = 'solved from here'; first success propagates up.
#   - Base case: processed all 81 cells → solved.
#
# =============================================================================
# ALGORITHM
# =============================================================================
#
# Backtracking (DFS):
#   At each empty cell, branch on 9 candidates. If a choice violates Sudoku
#   rules, skip it; else commit (mutate board + constraint sets), recurse to
#   the next cell index. If recursion reports failure, roll back (restore
#   board and bitmasks) — that's the "backtrack" step.
#
# Why it terminates:
#   LeetCode inputs have a solution; search explores a finite tree. Without a
#   solution, we exhaust branches and return False (not needed for LC tests).
#
# =============================================================================
# DATA STRUCTURES
# =============================================================================
#
# - board: 9×9 list of single-char strings '1'..'9' or '.'. Mutated in place.
#
# - rows[i], cols[j], boxes[k]: 9-bit integers (bitmask). Bit d is 1 iff digit
#   (d+1) is already used in that row/column/box. Example: rows[2] & (1 << 3)
#   means digit 4 is taken in row 2.
#
# - Box index: k = (r // 3) * 3 + (c // 3)  → 0..8, same layout as problem
#   statements usually draw grids.
#
# Alternatives you might mention in interview:
#   - sets of ints per row/col/box: clearer API, similar asymptotics.
#   - 9×9×9 boolean 'could place': more memory, same idea.
#   - bitmask chosen here: fast union/intersection, single machine integer.
#
# =============================================================================
# COMPLEXITY
# =============================================================================
#
# Time:  worst-case exponential in empty cells (branching up to 9). Not tight-
#   bounded; pruning makes real puzzles fast. For interviews: "exponential
#   worst case, problem-size constants make it practical."
# Space: O(1) extra if recursion depth ≤ 81 is treated as constant board size;
#   call stack O(81) = O(1) for fixed 9×9. Bitmasks are 9 ints each.
#
# =============================================================================
# EDGE CASES (mention in interview)
# =============================================================================
#
# - Already filled / no '.': dfs skips filled cells; hits cell==81 → True.
# - Invalid starting board: algorithm may explore everything and never succeed;
#   LeetCode assumes valid partial Sudoku. Production code might validate first.
# - Uniqueness: this finds *one* solution; Sudoku puzzles are designed for a
#   unique solution, but the code does not prove uniqueness.
# - Digit encoding: '1'..'9' map to bits 0..8 via 1 << (digit - 1).
#
# =============================================================================
# TESTING (what you'd say or implement in take-home)
# =============================================================================
#
# Unit tests:
#   - Known puzzle + snapshot of solved board (several published puzzles).
#   - Assert row/col/box constraints after solve (helper: no dupes 1–9).
# Property checks:
#   - Every cell is '1'..'9'; no '.' left.
#   - Each row, column, and 3×3 box contains exactly digits 1–9 once.
# Edge manual cases:
#   - Nearly complete grid (few empties) → fast path.
#   - Many empties → deeper search (still OK at 9×9).
# Stress:
#   - Time limit on worst official puzzle (optional; mainly for confidence).
#
# =============================================================================

# @lc code=start
from typing import List


class Solution:
    def solveSudoku(self, board: List[List[str]]) -> None:
        """
        Do not return anything, modify board in-place instead.

        Interview walkthrough of the implementation below:
          1) Seed row/col/box bitmasks from *given* digits so we never place a
             digit that conflicts with the initial puzzle.
          2) dfs(cell) scans indices 0..80 in order. Filled cells delegate to
             dfs(cell+1) without branching.
          3) For '.', merge masks: used = rows[r] | cols[c] | boxes[b]. Try each
             digit whose bit is not in `used`.
          4) Choose → OR bits into the three masks, recurse; on True, bubble up.
             On False or after exhausting digits, XOR bits off (same as clear for
             a single bit) and restore '.' — classic undo.
        """
        # One int per row/column/box: bit i set ⇔ digit (i+1) already placed there.
        rows = [0] * 9
        cols = [0] * 9
        boxes = [0] * 9

        # --- Initialize constraints from the givens (not '.'). ---
        for r in range(9):
            for c in range(9):
                ch = board[r][c]
                if ch == ".":
                    continue
                bit = 1 << (ord(ch) - ord("1"))
                b = (r // 3) * 3 + (c // 3)
                rows[r] |= bit
                cols[c] |= bit
                boxes[b] |= bit

        def dfs(cell: int) -> bool:
            # Processed every cell successfully → solved.
            if cell == 81:
                return True
            r, c = divmod(cell, 9)
            # Clue cell: no choice here; continue forward only.
            if board[r][c] != ".":
                return dfs(cell + 1)

            b = (r // 3) * 3 + (c // 3)
            # Union of forbidden digits from row, column, and 3×3 block.
            used = rows[r] | cols[c] | boxes[b]

            for d in range(9):
                bit = 1 << d
                if used & bit:
                    continue  # digit (d+1) conflicts with a peer

                # Place and push constraint updates (must undo if backtracking).
                board[r][c] = str(d + 1)
                rows[r] |= bit
                cols[c] |= bit
                boxes[b] |= bit

                if dfs(cell + 1):
                    return True

                # Backtrack: remove digit from board and all three masks.
                rows[r] ^= bit
                cols[c] ^= bit
                boxes[b] ^= bit
                board[r][c] = "."

            # No digit worked → trigger backtrack at caller.
            return False

        dfs(0)


# @lc code=end

