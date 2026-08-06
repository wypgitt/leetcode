#
# @lc app=leetcode id=1183 lang=python3
#
# [1183] Maximum Number Of Ones
#

# --- Interview notes (sliding-window constraint → residues, greedy, complexity, edges) ---
#
# Problem
# Fill an `height × width` binary matrix with as many `1`s as possible such that **every** contiguous `sideLength ×
# sideLength` submatrix contains **at most** `maxOnes` ones (`maxOnes` ≤ sideLength²).
#
# Structural lemma — one-one correspondence inside each square window
# Fix `L = sideLength`. Label rows `i ∈ [0, height-1]` and columns `j ∈ [0, width-1]`. Partition cells by residue pair
# `(i mod L, j mod L)`. There are exactly `L²` classes `C_{a,b}` for `a,b ∈ {0,…,L-1}`.
#
# Claim: **every** aligned `L × L` window (whether or not `L` divides the grid dimensions) contains **exactly one**
# cell from each class `C_{a,b}`.
#
# Sketch: A window with top-left `(r, c)` covers `(r + di, c + dj)` for `di,dj ∈ [0,L-1]`. As `(di,dj)` runs through
# all `L²` pairs, the residues `((r+di) mod L, (c+dj) mod L)` run through **all** `L²` residue pairs exactly once (product of
# two bijections on ℤ/Lℤ). Hence each window’s sum of entries equals “how many residue classes we globally set to all-1
# on their entire arithmetic lattice.”
#
# Consequence for the global optimum
# Let `x_{a,b} ∈ {0,1}` mean: every cell with `(i mod L, j mod L) = (a,b)` is `1`. Then **every** `L×L` window sum equals
# `Σ_{a,b} x_{a,b}` — the **same** value for all windows. The sliding constraint is therefore equivalent to:
#
#     Σ_{a,b} x_{a,b} ≤ maxOnes,
#
# i.e. we may turn **at most `maxOnes`** residue classes “on.” That many degrees of freedom are enough: no richer pattern
# beats picking **which** residue classes are active (periodic placement on each lattice).
#
# Counting cells per class
# Rows with `i ≡ a (mod L)` and `i ∈ [0, height-1]`: count
#     rowCnt(a) = ⌊(height - 1 - a) / L⌋ + 1   if `a < height`, else `0`.
# Similarly `colCnt(b)` using `width`. Class `(a,b)` has **rowCnt(a) · colCnt(b)** cells.
#
# Greedy choice
# To maximize total ones under “pick ≤ maxOnes` classes,” choose the classes with the **largest** cell counts (take the top
# `maxOnes` counts after sorting descending). If `maxOnes ≥ L²`, take all classes → entire matrix is achievable iff the
# uniform window sum `L²` ones never exceeds `maxOnes`… Actually when all `x=1`, window sum = `L²`, so we need `maxOnes ≥
# L²` to fill everything; otherwise cap at `maxOnes` classes.
#
# Algorithm
# 1. Enumerate all `(a,b) ∈ [0,L-1]²`, compute `freq[a,b] = rowCnt(a) * colCnt(b)`.
# 2. Sort `freq` descending (or use `nlargest`).
# 3. Sum the first `min(maxOnes, L²)` values (using only `L²` frequencies; extra budget does not help).
#
# Time complexity
# **O(L² log L²)** for sorting; `L = sideLength` (typically modest vs grid).
#
# Space complexity
# **O(L²)** for the frequency list.
#
# Edge cases
# • `maxOnes == 0` → return `0` (if allowed).
# • Very thin matrices: some `(a,b)` have zero cells — frequencies `0`; greedy ignores until needed.
# • `maxOnes ≥ L²` and constraint allows full fill only if window sum `L² ≤ maxOnes`; greedy adds all positive frequencies.
#
# Tests (sanity)
# • `width = height = 3`, `sideLength = 2`, `maxOnes = 1` → class sizes `4,2,2,1` → answer **4**.
# • `maxOnes` large enough to take all four classes → **9** ones (full `3×3`).
#
# Improvements
# • Avoid full sort: partial selection (`heapq.nlargest(maxOnes, freq)`), still **O(L² log maxOnes)**.
# • Closed form: frequencies are products `rowCnt(a)·colCnt(b)` — could sort row/col counts separately and merge for
#   theory; sorting `L²` numbers is simple in interviews.
#
# --- end notes ---

# @lc code=start
class Solution:
    def maximumNumberOfOnes(self, width: int, height: int, sideLength: int, maxOnes: int) -> int:
        L = sideLength

        def row_or_col_count(dim: int, residue: int) -> int:
            if residue >= dim:
                return 0
            return (dim - 1 - residue) // L + 1

        freq = []
        for a in range(L):
            ra = row_or_col_count(height, a)
            for b in range(L):
                rb = row_or_col_count(width, b)
                freq.append(ra * rb)

        freq.sort(reverse=True)
        return sum(freq[:maxOnes])


# @lc code=end
