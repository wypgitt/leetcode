#
# @lc app=leetcode id=3914 lang=python3
#
# [3914] Minimum Operations to Make Array Non Decreasing
#
# =============================================================================
# PROBLEM
# =============================================================================
#
# You may repeatedly choose a **subarray** nums[l..r] and add the **same**
# positive integer **x** to **every** element in that subarray. Each operation
# contributes **x** to the **total cost** (the objective is the **sum of all x**
# used, not the sum of per-index increases).
#
# Goal: make **nums** non-decreasing (**nums[i] <= nums[i+1]** for all i) with
# **minimum total cost**.
#
# =============================================================================
# MODELING ONE OPERATION TYPE (why “positive differences” appear)
# =============================================================================
#
# Only **increases** are allowed, so the final array **v** satisfies **v[i] >=
# nums[i]** coordinate-wise. Write the **deficit** (required increase)
#   **d[i] = v[i] - nums[i]  (>= 0)**.
#
# One operation adds **x** to indices **[l, r]** → it adds **x** to **d** on that
# entire segment. A sequence of operations produces **d** as a sum of such
# “rectangle” (interval) contributions; each operation’s **price** is **x**
# once, regardless of length.
#
# **Lemma (cost of realizing a fixed d).**  
# For nonnegative **d**, the **minimum sum of x** over all decompositions of
# **d** into interval additions equals
#
#   **C(d) = Σ_i max(0, d[i] − d[i−1])**,   with **d[−1] = 0**.
#
# **Sketch.**  
# Think of **d** as heights. Adding **x** to **[l, r]** raises a contiguous
# plateau by **x**; it is “paid” once at the **left edge** where height jumps up
# relative to the previous index (unless continuing an existing plateau). Formally,
# the **discrete derivative** **u[i] = d[i] − d[i−1]** must be covered: each
# positive **u[i]** needs at least **u[i]** units of new mass starting at **i**,
# and each operation creates matching mass at one left endpoint. Negative steps
# “reuse” earlier operations (no extra cost). Summing positive jumps yields **C(d)**.
# (This is the same idea as representing a piecewise-constant **d** with the
# minimum sum of uniform interval heights.)
#
# =============================================================================
# CHOOSING THE TARGET ARRAY v
# =============================================================================
#
# We must pick **v** non-decreasing and **v >= nums** to minimize **C(v − nums)**.
#
# Let **v*** be the **pointwise smallest** non-decreasing array with **v[i] >=
# nums[i]** — the **non-decreasing majorant** of **nums**:
#
#   **v[0] = nums[0]**,  
#   **v[i] = max(nums[i], v[i−1])**  for **i >= 1**.
#
# Any feasible **v** satisfies **v[i] >= v*[i]** (induction: **v[i] >= nums[i]**
# and **v[i] >= v[i−1] >= v*[i−1]** ⇒ **v[i] >= max(nums[i], v*[i−1]) = v*[i]**).
# Larger **v** only increases **d** in a way that does not decrease **C(d)** in
# this setup (standard “majorize” argument for this convex-like cost), so **v***
# is optimal. **Intuition:** extra increase beyond necessity wastes cost without
# fixing new violations.
#
# =============================================================================
# FINAL FORMULA
# =============================================================================
#
# 1. Sweep **i = 0..n−1**: **cur_v = max(nums[i], cur_v)** (with **cur_v** holding
#    **v[i]**).
# 2. **cur_d = cur_v − nums[i]** (deficit at **i**).
# 3. Accumulate **max(0, cur_d − prev_d)** where **prev_d** is **d[i−1]** (and
#    **prev_d = 0** before **i = 0** captures **max(0, d[0])** when folded into
#    the first iteration — see code).
#
# **Time O(n)**, **space O(1)** extra (only a few scalars).
#
# =============================================================================
# EDGE CASES
# =============================================================================
#
# - **n = 1**: already non-decreasing → **0**.
# - **Already non-decreasing**: **v[i] = nums[i]**, all **d[i] = 0** → **0**.
# - **Strict decreases**: **v** lifts the suffix; cost comes from **drops** in
#   **nums** (each “cliff” contributes through positive steps of **d**).
#
# =============================================================================
# TESTING
# =============================================================================
#
# - Brute for **n <= 8**: enumerate small integer **x** operations is messy; easier
#   to verify **C(d)** formula against known decompositions, and **v*** against
#   brute **v** search for random **nums** (small **n**, small values).
# - Cross-check full algorithm vs **O(n)** reference using explicit **d** array.
#
# =============================================================================
# IMPROVEMENTS / VARIANTS
# =============================================================================
#
# - **O(1) space** streaming version (below).
# - If the problem allowed **decreases**, the model would change entirely.
# - Related: “minimum operations” with **unit** range adds counts operations, not
#   sum of **x** — different objective.
#
# =============================================================================

# @lc code=start
from typing import List


class Solution:
    def minOperations(self, nums: List[int]) -> int:
        """
        Minimum sum of x over operations 'add x to a subarray [l..r]' to make nums
        non-decreasing. Equivalent to: build smallest non-decreasing majorant v,
        d[i]=v[i]-nums[i], answer = sum_i max(0, d[i]-d[i-1]).
        """
        if len(nums) == 1:
            return 0

        cur_v = nums[0]
        prev_d = cur_v - nums[0]
        ans = max(0, prev_d)

        for i in range(1, len(nums)):
            cur_v = max(nums[i], cur_v)
            cur_d = cur_v - nums[i]
            ans += max(0, cur_d - prev_d)
            prev_d = cur_d

        return ans


# @lc code=end
