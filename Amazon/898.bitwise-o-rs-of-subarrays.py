#
# @lc app=leetcode id=898 lang=python3
#
# [898] Bitwise ORs of Subarrays
#

# =============================================================================
# INTERVIEW: ELEVATOR PITCH (~30 seconds)
# =============================================================================
#
# "We need distinct values of (subarray OR) over all contiguous subarrays. Naively
# that’s O(n³) — enumerate ends, starts, and OR the segment. OR only ever **sets**
# bits, never clears them, so for a **fixed right endpoint** there are only O(B)
# different OR results as the left border slides (B ≤ bit-width). Carry a small set
# ‘current ORs ending here’, update in O(size of set) per element, merge into a
# global distinct set — **O(n · B)** time, **O(answer)** space."
#
# =============================================================================
# PROBLEM (PRECISE)
# =============================================================================
#
# Given integer array `arr`, consider every **non-empty** contiguous subarray
# `arr[i:j+1]`. Compute the bitwise **OR** of each subarray’s elements. Return how
# **many distinct** integers appear among those OR results.
#
# =============================================================================
# WHY NAIVE ENUMERATION FAILS
# =============================================================================
#
# • **O(n²)** subarrays; each OR across length L costs **O(L)** if done naively → **O(n³)**
#   total — too slow for **n ≈ 10⁵**.
# • We only need **distinctness**, not multiplicity — suggests **incremental merging**
#   of candidate values rather than full scans.
#
# =============================================================================
# KEY OBSERVATION — OR IS MONOTONE IN THE LEFT BORDER
# =============================================================================
#
# Fix the **right** endpoint at index `r`. Let
#
#       F(r, i) = arr[i] | arr[i+1] | … | arr[r]   for i ≤ r.
#
# As **`i` decreases** (subarray lengthens leftward), `F(r, i)` can only **gain** bits
# OR-ing in more numbers — in terms of the integer value, it is **non-decreasing**
# in the bitwise sense (superset of set bits). Therefore as `i` walks left, `F(r,i)`
# changes only when **new bits flip on** — at most **B** times for **B**-bit integers
# (e.g. **≤ 32** for 32-bit inputs).
#
# So for each `r`, the set **`{ F(r,i) : i = 0…r }`** has **O(B)** distinct values,
# not **O(r)**.
#
# =============================================================================
# ALGORITHM — INCREMENTAL SET `cur`
# =============================================================================
#
# Maintain **`cur`** = set of all OR values of subarrays **ending at the previous**
# index (after processing `arr[r-1]`). When `arr[r]` arrives:
#
#   • Every old subarray ending at `r−1` extends by OR-ing `arr[r]` → value `y | x`
#     for each `y` in `cur`.
#   • The subarray consisting **only** of `arr[r]` contributes OR `x`.
#
# Update:
#
#       cur ← { x } ∪ { y | x for all y in old_cur }
#
# Union **all** `cur` into a global distinct set `ans`, then report **`len(ans)`**.
#
# =============================================================================
# DATA STRUCTURES
# =============================================================================
#
# • **`set` (hash set)** — deduplicates OR values automatically; **O(1)** average
#   insert / membership for integers.
# • **`cur`** holds **O(B)** integers per step in theory — small constant for fixed
#   bit-width.
#
# Alternatives: compact **sorted list** + dedupe (same asymptotics); **bitset** only
# if value universe tiny — here values can be large, so store explicit ints.
#
# =============================================================================
# TIME & SPACE COMPLEXITY
# =============================================================================
#
# Let **B** = number of bits in values (≤ **31** for LeetCode’s signed 32-bit inputs).
#
# • Each step: build new `cur` from old `cur` of size **O(B)** → **O(B)** work.
# • **n** steps → **O(n · B)** time; with **B** constant, **O(n)** in the typical
#   competitive-programming sense.
# • **Space:** **`ans`** stores every distinct OR ever seen — **O(|output|)** ≤ **O(n·B)**
#   worst case; **`cur`** is **O(B)** auxiliary per layer.
#
# =============================================================================
# EDGE CASES
# =============================================================================
#
# • **`n == 1`** — answer **1** (single OR = `arr[0]`).
# • **Repeated values** — `cur` and `ans` are sets; duplicates collapse.
# • **Zeros** — `0 | x = x`; sets still correct.
#
# =============================================================================
# TESTING (UNIT / REGRESSION)
# =============================================================================
#
# • `[1,2,4]` → OR results `{1,2,3,4,6,7}` → **6** distinct (match hand enumeration).
# • `[0]` → **1**.
# • Brute force **O(n²)** over small random arrays (bitwise OR with accumulate) vs
#   optimized counter — must agree.
#
# =============================================================================
# IMPROVEMENTS / VARIANTS
# =============================================================================
#
# • **List + manual dedupe** if set overhead matters (micro-optimization).
# • **Two-pointer on sorted unique chain** — possible but set solution is standard.
#
# =============================================================================

# @lc code=start
from typing import List, Set


class Solution:
    def subarrayBitwiseORs(self, arr: List[int]) -> int:
        """
        Count distinct bitwise-OR results over all non-empty contiguous subarrays.

        For each new element x, new ORs ending here are x alone and (old_or | x)
        for every old_or that ended at the previous index. Union into answer set.
        """
        ans: Set[int] = set()
        cur: Set[int] = set()

        for x in arr:
            cur = {x} | {y | x for y in cur}
            ans.update(cur)

        return len(ans)


# @lc code=end
