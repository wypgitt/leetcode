/*
 * @lc app=leetcode id=1017 lang=java
 *
 * [1017] Convert To Base -2
 */

/*
 * --- Interview notes (negative radix, digits 0/1, remainder fix, complexity, edges, verification) ---
 *
 * Problem
 * Given integer **`n`**, return its representation in **radix −2** (base −2): digits **`0`** and **`1`** only, no leading
 * zeros except the string **`"0"`** for **`n = 0`**.
 *
 * Mathematical setup
 * Value of string **`d_{k-1}…d_0`** in base **`b`** is **`Σ d_i · b^i`**. Here **`b = −2`**, so each step adds **`0`** or
 * **`(-2)^i`**.
 *
 * Repeated division algorithm (same spirit as positive bases)
 * Write **`n = q · (−2) + r`** with **`r ∈ {0, 1}`** (desired digits). Java integer division **`n / (−2)`** truncates toward
 * zero; remainder **`n % (−2)`** follows Java remainder rules (same sign as dividend often). If remainder is **`−1`**, it is
 * not a legal digit: normalize by **`r ← r + 2`** and **`q ← q + 1`** (borrow / carry adjustment) so **`n = q' · (−2) + r'`**
 * with **`r' ∈ {0,1}`**.
 *
 * Loop
 * • **`n == 0`** stop (special-case **`n == 0`** → **`"0"`** before loop).
 * • Else take **`r = n % (-2)`**, **`n /= -2`**, **`if (r < 0): r += 2; n += 1`**, append **`r`** as least-significant new digit (build
 * reversed bit string), **`n`** becomes next quotient.
 *
 * Output
 * Reverse appended digits — MSB last produced corresponds to highest power.
 *
 * Why not use **`Integer.toBinaryString`**
 * Built-ins assume nonnegative radix **2**; negative radix needs explicit iterative extraction.
 *
 * Time complexity **O(log |n|)** — each step strictly reduces **`|n|`** in the relevant sense; number of digits **Θ(log |n|)**
 * for **`|n| ≥ 1`**.
 *
 * Space complexity **O(log |n|)** for the result string (plus **O(1)** arithmetic variables).
 *
 * Edge cases
 * • **`n = 0`** — definition **`"0"`** (loop would otherwise yield empty string).
 * • Large **`|n|`** — Java `int` range applies; use `long` if promoted on platform.
 *
 * Correctness check (interview trick)
 * Evaluate **`Σ d_i (−2)^i`** left-to-right or right-to-left to verify against **`n`** on examples.
 *
 * Tests (sanity)
 * • **`n = 2`** → **`"110"`** since **`4 − 2 = 2`**.
 * • **`n = 3`** → **`"111"`** ( **`4 − 2 + 1`** ).
 *
 * Improvements
 * • Bit-twiddling variants exist for speed in fixed-width hardware — unnecessary in BigInt-style interviews.
 *
 * --- end notes ---
 */

// @lc code=start
class Solution {
    public String baseNeg2(int n) {
        if (n == 0) {
            return "0";
        }
        StringBuilder digits = new StringBuilder();
        while (n != 0) {
            int r = n % -2;
            n /= -2;
            if (r < 0) {
                r += 2;
                n += 1;
            }
            digits.append(r);
        }
        return digits.reverse().toString();
    }
}
// @lc code=end
