#
# @lc app=leetcode id=858 lang=python3
#
# [858] Mirror Reflection
#

# =============================================================================
# INTERVIEW: ELEVATOR PITCH (~30 seconds)
# =============================================================================
#
# "Model reflections by **unfolding** the square room into an infinite grid of copies.
# The laser becomes a **straight ray** from the southwest corner with slope **`q/p`**.
# The first time that ray hits a **lattice corner** of this tiling corresponds to hitting
# a receptor. Scaling by **`gcd(p,q)`** removes retracing the same rational slope; the
# **parity** of the reduced horizontal and vertical crossing counts tells us **which**
# corner (0, 1, or 2) is reached first — no simulation of bounces is needed."
#
# =============================================================================
# PROBLEM (PRECISE)
# =============================================================================
#
# A square room has **mirrors on all four walls**. The **southwest** corner has **no**
# receptor (that is where the laser starts). The other three corners have receptors:
#
#   • **`0`** — northwest (NW)
#   • **`1`** — northeast (NE)
#   • **`2`** — southeast (SE)
#
# The room has side length **`p`** (positive integer). From SW, the laser **first**
# strikes the **east** wall at a point whose distance **along that wall**, measured **down
# from receptor `0`** (the north end of the east wall), equals **`q`** (integer,
# **`1 ≤ q ≤ p`**).
#
# Return **`0`**, **`1`**, or **`2`** according to which receptor is hit **first** (the ray
# is guaranteed to terminate at some receptor).
#
# =============================================================================
# GEOMETRY — COORDINATES (MATCHING THE STATEMENT)
# =============================================================================
#
# Put **southwest** at **`(0, 0)`**, **`x`** increasing **east**, **`y`** increasing **north**.
# The square is **`[0, p] × [0, p]`**.
#
# **East wall:** **`x = p`**, **`y ∈ [0, p]`**. Receptor **`0`** is at **`(0, p)`** (NW); the
# **north** end of the east wall is **`(p, p)`** (NE), adjacent to **`0`** along the top edge.
# “Distance **`q`** from receptor **`0`**” along the east wall means: starting from **`(p, p)`**
# and walking **south** along **`x = p`**, the hit point is **`(p, p − q)`**.
#
# So the segment from **`(0, 0)`** to the **first** east-wall hit is aligned with the vector
# **`(p, p − q)`**, equivalently slope **`(p − q) / p`** toward increasing **`x`**. Many
# solutions instead reparameterize the **same ray** by scaling time so the first east-wall
# contact is **`(p, q)`** with **`y`** measured **from the south** — that is an affine change
# along the east wall only; **which corner is met first** is invariant under that bookkeeping.
#
# **LeetCode’s standard solution** uses the **`(p, q)`** parameterization (first east hit at
# height **`q`** above the **south** edge). Unfolding then tracks multiples of **`p`** in **`x`**
# and **`y`**; the **parity classification** below matches their tests.
#
# =============================================================================
# CORE IDEA — UNFOLDING (REPLACE REFLECTIONS WITH A STRAIGHT LINE)
# =============================================================================
#
# Instead of reflecting the laser, **reflect the room** across walls. The trajectory becomes a
# **straight half-line** through a **tiling** of **`p × p`** squares. Each time the unfolded
# path crosses a **vertical grid line** **`x = k·p`**, that corresponds to meeting an **east or
# west** wall in the real room; each **horizontal** crossing **`y = k·p`** corresponds to a
# **north or south** wall hit.
#
# The laser **first returns to a corner receptor** at the **smallest positive** scaling where
# the unfolded ray lands exactly on a **corner** of the **`p`-grid** — i.e. when both
# coordinates are integer multiples of **`p`** at the same “time” along the primitive direction.
#
# Write the direction after clearing the common divisor **`g = gcd(p, q)`**:
#
#     **`p' = p / g`**,   **`q' = q / g`**   (coprime integers)
#
# Think of **`p'`** as the number of **room widths** (east–west periods) and **`q'`** as the
# number of **room heights** (north–south periods) along the primitive rational slope before the
# unfolded path hits a **lattice corner** of the **`p × p`** tiling (equivalently: before the
# reduced ray hits **`(integer · p, integer · p)`** in unfolded coordinates).
#
# =============================================================================
# PARITY RULE (THE WHOLE ALGORITHM)
# =============================================================================
#
# After **`p ← p'`**, **`q ← q'`**:
#
#   1. If **`p` is even** → receptor **`2`** (SE).
#   2. Else if **`q` is even** → receptor **`0`** (NW).
#   3. Else (**both odd**) → receptor **`1`** (NE).
#
# **Why this matches examples**
#
#   • **`p = 2, q = 1`** → **`gcd = 1`**, **`p = 2`** even → **`2`** (problem example 1).
#   • **`p = 3, q = 1`** → **`p, q`** odd → **`1`** (example 2).
#
# **Why no fancy data structures:** this is **`O(log min(p,q))`** arithmetic from Euclidean
# gcd — constant memory.
#
# =============================================================================
# WHY `gcd` FIRST — PERIODICITY / REDUCE TO A PRIMITIVE STEP
# =============================================================================
#
# The ray’s slope is **`q/p`**. Write **`q/g`** and **`p/g`** with **`g = gcd(p,q)`**. Before the
# path hits any receptor, it repeats the same **local pattern** every **`g`** copies along the
# rational generator — reducing **`(p,q)`** by **`gcd`** answers **which receptor type** appears
# first without counting redundant loops.
#
# Equivalently: in lowest terms **`q'/p'`**, the first corner hit corresponds to **coprime**
# **`(p', q')`**; parity of **`p'`** and **`q'`** encodes **which folded corner** aligns first.
#
# =============================================================================
# TIME & SPACE COMPLEXITY
# =============================================================================
#
# • **Time:** **`O(log min(p, q))`** for Euclidean **`gcd`** (constraints **`p ≤ 1000`** → tiny).
# • **Space:** **`O(1)`** beyond inputs.
#
# =============================================================================
# EDGE CASES & SANITY CHECKS
# =============================================================================
#
# • **`q = p`:** **`gcd = p`**, reduced **`(1, 1)`** → both odd → **`1`** (NE). The first east-wall
#   hit is the **NE** corner — receptor **`1`**.
# • **`q = 1`**, **`p` odd:** reduced **`(p, 1)`** → **`q`** odd; if **`p`** odd → **`1`**.
# • **`p` even**, **`q`** odd after reduction: **`2`** (e.g. **`p=2,q=1`**).
# • Constraints guarantee termination; no floating-point — **pure integers**.
#
# =============================================================================
# IMPROVEMENTS / ALTERNATIVES (INTERVIEW TALKING POINTS)
# =============================================================================
#
# • **Simulation:** For tiny **`p`**, one could simulate wall bounces with rationals — **slower**
#   and **error-prone**; unfolding + gcd is the **standard** answer.
# • **Binary gcd** (optional): asymptotically similar for these bounds.
# • If **`p, q`** were huge, still only **`gcd`** + parity — **no** change in asymptotics.
#
# =============================================================================
# TESTS (MENTAL / MANUAL)
# =============================================================================
#
# | `(p, q)` | `gcd` | reduced `(p',q')` | output |
# |----------|-------|-------------------|--------|
# | (2, 1)   | 1     | (2, 1) p even     | **2**  |
# | (3, 1)   | 1     | (3, 1) both odd   | **1**  |
# | (1, 1)   | 1     | (1, 1) both odd   | **1**  |
# | (4, 2)   | 2     | (2, 1) p even     | **2**  |
# | (3, 2)   | 1     | (3, 2) q even     | **0**  |
#
# =============================================================================

import math

# @lc code=start
class Solution:
    def mirrorReflection(self, p: int, q: int) -> int:
        g = math.gcd(p, q)
        p //= g
        q //= g
        if p % 2 == 0:
            return 2
        if q % 2 == 0:
            return 0
        return 1


# @lc code=end

if __name__ == "__main__":
    f = Solution().mirrorReflection
    assert f(2, 1) == 2
    assert f(3, 1) == 1
    assert f(1, 1) == 1
    assert f(4, 2) == 2
    assert f(3, 2) == 0
