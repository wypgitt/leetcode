#
# @lc app=leetcode id=2647 lang=python3
#
# [2647] Color the Triangle Red
#

# --- Notes (problem, geometry, propagation, pattern, algorithm, complexity, interview) ---
#
# Problem restatement
# An equilateral triangle of side length n is subdivided into n^2 unit equilateral triangles.
# Row i (1-indexed) contains 2*i - 1 unit triangles, indexed (i, 1) .. (i, 2*i - 1). Two unit
# triangles are neighbors iff they share an edge (not merely a vertex).
# Initially all units are white. You choose an initial set of k unit triangles to color red. Then
# repeatedly: pick any white triangle that has at least two red neighbors, color it red, repeat
# until no such white triangle exists.
# Goal: use the minimum possible k such that this process eventually colors every unit triangle red.
# Return the list of coordinates (row, col) of any optimal initial set (smallest size; any tie).
#
# Why not simulate BFS from many seeds?
# Brute force search for minimum seed set is exponential. The intended solution is a closed-form
# constructive pattern discovered by observing how “two red neighbors” propagation spreads on the
# triangular lattice when seeding bottom rows with periodic density.
#
# Observed structure (editorial / solutions)
# The apex (1, 1) must be seeded — it has few neighbors, so it cannot turn red only via propagation
# from below without ever being red itself in minimal constructions.
# Processing rows from the bottom (row n) upward toward row 2, the optimal seeding follows a
# 4-row cycle in the phase of which kind of row we paint:
#   k == 0 (bottom-most phase of each block): seed all ODD columns in that row: (i, 1), (i, 3), ...
#   k == 1: seed a single cell (i, 2) — the even slot that propagates into the interior.
#   k == 2: seed odd columns starting from 3: (i, 3), (i, 5), ... (complements k == 0 on alternate rows).
#   k == 3: seed only (i, 1).
# After handling rows n down to 2, row 1 is only the apex; include [1, 1] once.
# Phase index k advances k <- (k + 1) % 4 after each row.
#
# Algorithm (constructive)
# - ans <- [[1, 1]]
# - k <- 0
# - for i from n down to 2 (descending):
#     append cells per k (nested loops for odd columns using range step 2)
#     k <- (k + 1) % 4
# - return ans
#
# Correctness (high level)
# Proofs are lengthy; contest/editorial reduces to invariant propagation covering all interior cells
# without redundant seeds. Trust OJ-verified pattern or formalize as invariant exercise.
#
# Time complexity
# Rows processed: O(n). Some phases append O(i) cells on row i -> sum_i O(i) = O(n^2) worst-case output size.
#
# Space complexity
# O(n^2) for the answer list (required); O(1) auxiliary beyond output.
#
# Edge cases
# - n == 1: only [[1, 1]].
# - n == 2: apex plus full odd positions on row 2 per first downward iteration.
#
# Improvements / variants
# - Walkccc’s alternate formulation chunks by (n % 4) prefix + 4-row blocks — same idea, different loop shape.
#
# LeetCode submission
# `from typing import List` inside # @lc code=start.
#
# Interview walkthrough
# 1) Encode neighbor geometry on triangular grid.
# 2) Recognize irrelevance of simulating greedy fill from arbitrary seeds at scale.
# 3) Present periodic bottom-up seed pattern and O(n^2) generation.
# --- end notes ---

# @lc code=start
from typing import List


class Solution:
    def colorRed(self, n: int) -> List[List[int]]:
        ans: List[List[int]] = [[1, 1]]
        k = 0
        for i in range(n, 1, -1):
            if k == 0:
                for j in range(1, i << 1, 2):
                    ans.append([i, j])
            elif k == 1:
                ans.append([i, 2])
            elif k == 2:
                for j in range(3, i << 1, 2):
                    ans.append([i, j])
            else:
                ans.append([i, 1])
            k = (k + 1) % 4
        return ans


# @lc code=end
