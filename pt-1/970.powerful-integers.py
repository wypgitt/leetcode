#
# @lc app=leetcode id=970 lang=python3
#
# [970] Powerful Integers
#

# --- Interview notes (enumeration, geometric growth, set dedup, edge cases, complexity) ---
#
# Problem
# Given integers **`x`**, **`y`**, and **`bound`**, collect every integer **`n`** such that **`n = x^i + y^j`** for some integers
# **`i ≥ 0`**, **`j ≥ 0`**, and **`n ≤ bound`**. Return the values in **any order** (duplicates removed).
#
# Observations
# • **Nonnegative exponents** — **`x^0 = y^0 = 1`**, so the smallest possible sum is **`1 + 1 = 2`** when **`x, y ≥ 1`** (as in the
#   usual constraints). Thus **`bound < 2`** ⇒ **empty** answer.
# • **Uniqueness** — the same integer may arise from different **`(i, j)`** pairs (e.g. **`2^1 + 2^0 = 2^0 + 2^1`**), so **dedup**
#   with a **`set`** (or sort + unique) is natural.
# • **Finite search space** — for **`x ≥ 2`**, **`x^i`** grows exponentially; **`x^i > bound`** ⇒ for any **`y^j ≥ 1`**,
#   **`x^i + y^j > bound`**. So only finitely many **`i`** (and symmetrically **`j`**) matter. For **`x == 1`**, **`1^i = 1`**
#   for all **`i`** — treat as **one** power value and **stop** to avoid an infinite loop.
#
# Algorithm
# 1. **`powers(v, bound)`** — list all **`v^k ≤ bound`** for **`k = 0, 1, …`**, breaking after **`k = 0`** if **`v == 1`**.
# 2. **`Px = powers(x, bound)`**, **`Py = powers(y, bound)`**.
# 3. For each **`a ∈ Px`**, **`b ∈ Py`**, if **`a + b ≤ bound`**, insert **`a + b`** into a **`set`**.
# 4. Return **`list(set)`** (order irrelevant).
#
# Why not scan all **`i, j`** up to a huge cap?
# Bounding **`x^i`** by **`bound`** directly limits exponents — clearer and matches the math (**`O(log bound)`** layers for
# **`x ≥ 2`**).
#
# Data structures
# • **`list`** for power lists — small (**`O(log bound)`** elements).
# • **`set`** for distinct sums — up to **`|Px|·|Py|`** insertions, typically modest.
#
# Time complexity
# • **`|Px| = O(log_x bound)`** for **`x ≥ 2`**, **`O(1)`** if **`x = 1`**.
# • **`|Py|`** similarly.
# • Nested loops: **`O(|Px| · |Py|)`**, which is **`O((log bound)^2)`** for fixed **`x, y ≥ 2`** — easily fits **`bound ≤ 10^6`**.
#
# Space complexity
# **`O(|Px| · |Py|)`** for the set of sums in the worst case (plus **`O(|Px| + |Py|)`** for power lists). Output size is at most the
# same order as distinct sums **≤ bound**, hence **`O(bound)`** in a trivial worst case but **sparse** in practice.
#
# Edge cases
# • **`bound < 2`** — **no** sum **`≤ bound`** with **`x, y ≥ 1`** ⇒ **`[]`**.
# • **`x == 1` or `y == 1`** — **single** representative power (**`1`**) for that base; avoid infinite **`i`** loop.
# • **`bound`** exactly equals some **`x^i + y^j`** — include it (**`≤`**).
#
# Tests (quick)
# • **`x = 2`, `y = 3`, `bound = 10`** — e.g. **`2 + 3 = 5`**, **`4 + 9 = 13 > 10`** excluded; includes **`5`**, **`7`**, **`9`**, etc.
# • **`x = 1`, `y = 1`, `bound = 3`** — only **`1 + 1 = 2`** ⇒ **`[2]`**.
#
# Improvements
# • **Sorted output** — **`sorted(ans)`** if the interviewer wants deterministic behavior (**`O(k log k)`** on output size **`k`**).
# • **Early inner break** — if **`Px`** sorted ascending and **`Py`** sorted, for fixed **`a`** binary-search largest **`b`** with
#   **`a + b ≤ bound`** — usually unnecessary given tiny exponent lists.
#
# --- end notes ---

# @lc code=start
from typing import List


class Solution:
    def powerfulIntegers(self, x: int, y: int, bound: int) -> List[int]:
        def powers(base: int) -> List[int]:
            out = []
            v = 1
            while v <= bound:
                out.append(v)
                if base == 1:
                    break
                v *= base
            return out

        px, py = powers(x), powers(y)
        seen = set()
        for a in px:
            for b in py:
                s = a + b
                if s <= bound:
                    seen.add(s)
        return list(seen)


# @lc code=end
