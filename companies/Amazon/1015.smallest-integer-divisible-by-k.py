#
# @lc app=leetcode id=1015 lang=python3
#
# [1015] Smallest Integer Divisible By K
#

# --- Interview notes (repunits, modular recurrence, 2/5 impossibility, pigeonhole, complexity) ---
#
# Problem
# Find the **length** of the **smallest** positive integer whose decimal representation uses **only digit `1`** (a **repunit**:
# `1, 11, 111, …`) and which is divisible by **`K`**. If none exists, return **`-1`**.
#
# Representative notation
# Let **`R_n`** be the integer with **`n`** copies of digit **`1`**. Then **`R_{n+1} = R_n · 10 + 1`**. Working modulo **`K`**:
# **`r_{n+1} ≡ (r_n · 10 + 1) mod K`**, with **`r_1 ≡ 1`**. The smallest **`n`** with **`r_n ≡ 0 (mod K)`** is the answer’s length.
#
# When is it impossible?
# • Any repunit ends in **`1`**, hence it is **odd** ⇒ divisible by **`2`** never.
# • Last digit **`1`** ⇒ not divisible by **`5`**.
# So if **`K`** shares a factor **`2`** or **`5`** with **`10`**—equivalently **`K % 2 == 0`** or **`K % 5 == 0`**—no repunit can be a multiple of **`K`** ⇒ **`-1`** immediately.
#
# Why try at most **`K`** lengths (pigeonhole)
# Remainders modulo **`K`** lie in **`{0,…,K−1}`**. While scanning **`n = 1, 2, …`**, either some **`r_n = 0`** (done) or some remainder repeats before hitting **`0`**. If **`gcd(K,10)=1`** (here ensured once **`2∤K`** and **`5∤K`**), standard theory guarantees a solution exists and the first zero appears within **`K`** steps; the explicit loop bound **`K`** matches the editorial bound on iterations.
#
# Algorithm
# 1. If **`K % 2 == 0`** or **`K % 5 == 0`**, return **`-1`**.
# 2. **`r = 0`**. For **`n`** from **`1`** to **`K`**: **`r = (r * 10 + 1) % K`**; if **`r == 0`**, return **`n`**.
# 3. Return **`-1`** (should not occur under usual constraints after step 1).
#
# Data structures
# Only integers **`r`** and **`n`** — **no arrays or hash tables**.
#
# Time complexity **O(K)** — at most **`K`** modular updates.
#
# Space complexity **O(1)**.
#
# Edge cases
# • **`K == 1`** — **`"1"`** works → length **1**.
# • **`K`** prime other than **`2, 5`** — algorithm finds minimal **`n ≤ K`** when solution exists.
#
# Tests (sanity)
# • **`K = 1`** → **1**.
# • **`K = 3`** → **`111`** → **3**.
# • **`K = 2`** or **`K = 10`** → **-1**.
#
# Improvements
# • Mathematical shortcuts using multiplicative order of **`10`** modulo **`K`** exist for theory — unnecessary for coding interviews given **`K ≤ 10⁴`** style bounds.
#
# --- end notes ---

# @lc code=start
class Solution:
    def smallestRepunitDivByK(self, k: int) -> int:
        if k % 2 == 0 or k % 5 == 0:
            return -1
        r = 0
        for n in range(1, k + 1):
            r = (r * 10 + 1) % k
            if r == 0:
                return n
        return -1


# @lc code=end
