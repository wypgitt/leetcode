/*
 * @lc app=leetcode id=1006 lang=java
 *
 * [1006] Clumsy Factorial
 */

/*
 * --- Interview notes (pattern * / + - , precedence, stack as “terms”, division trap, complexity) ---
 *
 * Problem
 * Define `clumsy(n)` by writing numbers `n, n-1, …, 1` in order and inserting operators in a repeating cycle
 * `*, /, +, -, *, /, +, -, …` between them (first operator between `n` and `n-1` is `*`).
 * Evaluate using normal arithmetic rules: **all `*` and `/` are done before `+` and `-`**, and within each group,
 * `*` and `/` associate **left to right**. Division is integer division with truncation **toward zero** (same as applying
 * `(int)(a / b)` in Java for each `/` step — Python `//` floors toward −∞ and differs on negative intermediates).
 *
 * Example
 * `clumsy(10) = 10 * 9 / 8 + 7 - 6 * 5 / 4 + 3 - 2 * 1` → after mul-div passes: `(10*9/8) + 7 - (6*5/4) + 3 - (2*1)` → **12**.
 *
 * Why a stack (not one giant string eval)
 * After respecting precedence, the expression becomes an alternating sum of **blocks**, each block being a left-to-right
 * chain of `*` and `/` applied to a contiguous descending run of integers. A stack lets us fold each mul-div chain into a
 * single number on the top, push terms for `+`, and push **negated** starts for `-` so that the next `*` attaches to the
 * correct block (including negative chains like `- 6 * 5 / 4`).
 *
 * Simulation (operator index `k mod 4`)
 * Start `stk = [n]`. For `x` from `n-1` down to `1`:
 * • `k == 0` (`*`): `top *= x`
 * • `k == 1` (`/`): `top = (int)(top / x)` — truncate toward zero
 * • `k == 2` (`+`): push `x` as a new positive term
 * • `k == 3` (`-`): push `-x` so the following mul and div apply to a negative base for that block
 * Then `k = (k + 1) % 4`.
 * Answer = **sum(stk)** (stack holds disjoint signed terms).
 *
 * Division pitfall (Python vs Java)
 * Use **`(int)((double)a / b)`** or integer truncation toward zero: in Java, `/` on ints truncates toward zero. When using
 * long arithmetic, apply `(long)a / b` then cast. For positives, Java int division matches floor; when the numerator becomes
 * negative (from a leading `-` before a block), Python `//` and truncation toward zero **diverge**. LeetCode follows
 * truncation toward zero for `/`.
 *
 * Time complexity **O(n)** — one pass over `n-1` operators.
 *
 * Space complexity **O(n)** — stack size bounded by **O(n)** (many separate `+/-` terms in worst case).
 *
 * Edge cases
 * • `n == 1` — only `stk = [1]` → **1**.
 * • Large `n` (up to `10^4`) — linear pass is fine.
 *
 * Tests (statement)
 * • `n = 4` → **7** (`4 * 3 / 2 + 1`).
 * • `n = 10` → **12**.
 *
 * Improvements
 * • **Closed form** exists by grouping every block of four numbers — possible **O(1)** or **O(log n)** math for contests;
 *   stack simulation is the standard interview presentation.
 * • Could accumulate running sum without storing full stack if only sum needed — still **O(1)** extra variables but less
 *   clear than explicit stack.
 *
 * --- end notes ---
 */

import java.util.ArrayDeque;
import java.util.Deque;

// @lc code=start
class Solution {
    public int clumsy(int n) {
        Deque<Integer> stk = new ArrayDeque<>();
        stk.addLast(n);
        int k = 0;
        for (int x = n - 1; x >= 1; x--) {
            if (k == 0) {
                stk.addLast(stk.pollLast() * x);
            } else if (k == 1) {
                int top = stk.pollLast();
                stk.addLast(truncDivTowardZero(top, x));
            } else if (k == 2) {
                stk.addLast(x);
            } else {
                stk.addLast(-x);
            }
            k = (k + 1) % 4;
        }
        int sum = 0;
        for (int v : stk) {
            sum += v;
        }
        return sum;
    }

    /** Integer division truncating toward zero (matches Python `int(a/b)` for `/`). */
    private static int truncDivTowardZero(int a, int b) {
        return a / b;
    }
}
// @lc code=end
