#
# @lc app=leetcode id=1006 lang=python3
#
# [1006] Clumsy Factorial
#

# --- Interview notes (pattern */+- , precedence, stack as “terms”, division trap, complexity) ---
#
# Problem
# Define `clumsy(n)` by writing numbers `n, n-1, …, 1` in order and inserting operators in a repeating cycle
# `*, /, +, -, *, /, +, -, …` between them (first operator between `n` and `n-1` is `*`).
# Evaluate using normal arithmetic rules: **all `*` and `/` are done before `+` and `-`**, and within each group,
# `*` and `/` associate **left to right**. Division is integer division with truncation **toward zero** (same as applying
# `int(a / b)` in Python for each `/` step — **not** `//`, which floors toward −∞ and differs on negative intermediates).
#
# Example
# `clumsy(10) = 10 * 9 / 8 + 7 - 6 * 5 / 4 + 3 - 2 * 1` → after `*`/`/` passes: `(10*9/8) + 7 - (6*5/4) + 3 - (2*1)` → **12**.
#
# Why a stack (not one giant string eval)
# After respecting precedence, the expression becomes an alternating sum of **blocks**, each block being a left-to-right
# chain of `*` and `/` applied to a contiguous descending run of integers. A stack lets us fold each `*/` chain into a
# single number on the top, push terms for `+`, and push **negated** starts for `-` so that the next `*` attaches to the
# correct block (including negative chains like `- 6 * 5 / 4`).
#
# Simulation (operator index `k mod 4`)
# Start `stk = [n]`. For `x` from `n-1` down to `1`:
# • `k == 0` (`*`): `top *= x`
# • `k == 1` (`/`): `top = int(top / x)` — truncate toward zero
# • `k == 2` (`+`): push `x` as a new positive term
# • `k == 3` (`-`): push `-x` so the following `*`/`/` apply to a negative base for that block
# Then `k = (k + 1) % 4`.
# Answer = **sum(stk)** (stack holds disjoint signed terms).
#
# Division pitfall (Python)
# Use **`int(a / b)`** for each `/`. For positives, `int(a/b)` equals `a // b`. When the numerator becomes negative (from a
# leading `-` before a block), `//` and `int()` **diverge** (e.g. `-30 // 4 == -8` but `int(-30/4) == -7`). LeetCode follows
# truncation toward zero for `/`.
#
# Time complexity **O(n)** — one pass over `n-1` operators.
#
# Space complexity **O(n)** — stack size bounded by **O(n)** (many separate `+/-` terms in worst case).
#
# Edge cases
# • `n == 1` — only `stk = [1]` → **1**.
# • Large `n` (up to `10^4`) — linear pass is fine.
#
# Tests (statement)
# • `n = 4` → **7** (`4 * 3 / 2 + 1`).
# • `n = 10` → **12**.
#
# Improvements
# • **Closed form** exists by grouping every block of four numbers — possible **O(1)** or **O(log n)** math for contests;
#   stack simulation is the standard interview presentation.
# • Could accumulate running sum without storing full stack if only sum needed — still **O(1)** extra variables but less
#   clear than explicit stack.
#
# --- end notes ---

# @lc code=start
class Solution:
    def clumsy(self, n: int) -> int:
        stk = [n]
        k = 0
        for x in range(n - 1, 0, -1):
            if k == 0:
                stk.append(stk.pop() * x)
            elif k == 1:
                stk.append(int(stk.pop() / x))
            elif k == 2:
                stk.append(x)
            else:
                stk.append(-x)
            k = (k + 1) % 4
        return sum(stk)


# @lc code=end
