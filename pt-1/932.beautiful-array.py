#
# @lc app=leetcode id=932 lang=python3
#
# [932] Beautiful Array
#

# --- Interview notes (no arithmetic progression in index order, divide & conquer, doubling trick) ---
#
# Problem
# Return **any** permutation of **`1 … n`** such that for **every** triple of indices **`i < j < k`**,
# **`A[i] + A[k] ≠ 2 · A[j]`** — equivalently **no three positions** (in **sequence order**) form an **arithmetic progression** in the
# **values** (**middle index** **`j`** is the arithmetic mean of **`A[i]`** and **`A[k]`**).
#
# Structural idea — separate odds and evens
# If **`x`** is odd and **`y`** is even, **`(x + y) / 2`** is **not an integer**, so **no** integer can be the **mean** of one odd and one
# even value. Thus any triple mixing **odd-only** and **even-only** middle constraints interacts cleanly when we **partition** by parity.
# The classical construction repeatedly maps a beautiful array **`B`** of length **`m`** into **`[2b−1 for b in B] + [2b for b in B]`** — odds
# first, then evens — doubling the length while preserving the **beautiful** property by induction (proof sketched in editorials: AP
# contradictions fall into cases across the split).
#
# Algorithm (iterative doubling — same recursion unrolled)
# 1. Start **`ans = [1]`** (trivially beautiful for **`n = 1`**).
# 2. While **`len(ans) < n`**: replace **`ans`** with **`[2·x − 1 for x in ans] + [2·x for x in ans]`** (odds then evens of the scaled copy).
# 3. When **`len(ans) ≥ n`**, output **`[x for x in ans if x ≤ n][:n]`** — keep **order**, drop values **`> n`**, take the **first **`n`**
#    numbers** (they form **`1 … n`** exactly for this construction).
#
# Why this yields a permutation of **`1…n`**
# The process generates a **specific** ordering of **`1 … 2^k`** for **`2^k ≥ n`**; filtering **`x ≤ n`** in order keeps **`n`**
# **distinct** integers from **`{1,…,n}`** (standard result for this template).
#
# Data structures
# **`list`** only — no hash structures needed.
#
# Time complexity **`O(n)`** — total size across doublings is **`1 + 2 + 4 + … + O(n) = O(n)`** work (last layer dominates).
#
# Space complexity **`O(n)`** for the built list before filtering.
#
# Edge cases
# • **`n == 1`** — **`[1]`**.
#
# Tests (sanity)
# • **`n = 4`** → e.g. **`[1, 3, 2, 4]`** (not unique — other beautiful arrays exist).
#
# Improvements
# • **Recursive** version matches interviews that prefer **`f(n) → odds(f(⌈n/2⌉)) + evens(f(⌊n/2⌋))`** style (same **`O(n)`** idea with
#   careful slicing).
# • Optional **validator**: check all **`i < j < k`** in **`O(n³)`** for small **`n`** when debugging.
#
# --- end notes ---

# @lc code=start
from typing import List


class Solution:
    def beautifulArray(self, n: int) -> List[int]:
        ans = [1]
        while len(ans) < n:
            ans = [2 * x - 1 for x in ans] + [2 * x for x in ans]
        return [x for x in ans if x <= n][:n]


# @lc code=end
