/*
 * @lc app=leetcode id=233 lang=java
 *
 * [233] Number of Digit One
 */

/*
 * =============================================================================
 * PROBLEM (precise)
 * =============================================================================
 *
 * Given an integer n >= 0, count how many times the digit **1** appears in the
 * decimal representation of **all** integers from **1** through **n** inclusive.
 * (Do not treat “1” as a string problem over arbitrary bases unless stated.)
 *
 * =============================================================================
 * WHY NOT BRUTE FORCE
 * =============================================================================
 *
 * Enumerating every k in [1, n] and counting ‘1’ digits costs **O(n log n)** total
 * digit work — **too slow** when n approaches 2^31 − 1 (LeetCode-scale inputs).
 *
 * We need **digit-pattern math**: fix each decimal position independently and add
 * contributions in **O(number of digits)** = **O(log10 n)** time with **O(1)** extra
 * space — no arrays proportional to n.
 *
 * =============================================================================
 * CORE IDEA (count ‘1’ per position)
 * =============================================================================
 *
 * Consider one decimal position with weight **factor** ∈ {1, 10, 100, …}. Split n
 * into three conceptual parts relative to that position:
 *
 *   higher   = digits left of this position   = n // (factor * 10)
 *   current  = digit at this position        = (n // factor) % 10
 *   lower    = digits right of this position = n % factor
 *
 * Example: n = 3_1_4 with factor = 10 → higher = 3, current = 1, lower = 4.
 *
 * Now reason how many times digit 1 appears **at this position** for all numbers in
 * [0, n] (then adjust for problem range [1, n] if needed — the standard formula
 * counts [0, n] and **subtracts** the zero case; see code note).
 *
 * Actually common LeetCode formulation counts [0,n] for digit positions and the
 * contribution formulas give total ‘1’s for numbers from 0 to n inclusive. Since 0
 * contributes **no** digit ‘1’, **answer([1,n]) = answer([0,n])**.
 *
 * Case analysis at this position (classic):
 *
 * - **current == 0:** The digit at this position cycles through 0..9 as `higher`
 *   runs. Full cycles of ‘1’ at this slot occur **higher** times, each contributing
 *   **factor** occurrences → **higher * factor**.
 *
 * - **current == 1:** Same full cycles from higher, plus a **partial** tail where the
 *   digit is stuck at 1 while `lower` runs 0..lower → extra **lower + 1** ones.
 *   Total **higher * factor + lower + 1**.
 *
 * - **current >= 2:** We get **higher + 1** full blocks where this digit hits 1 at
 *   least once per block width → **(higher + 1) * factor**.
 *
 * Summing over factors 1, 10, 100, … while factor <= n yields the answer.
 *
 * This is the standard **per-digit enumeration** trick — interviewers often accept the
 * three-case formula after you derive it once on the board for a fixed factor.
 *
 * =============================================================================
 * DATA STRUCTURES
 * =============================================================================
 *
 * **None** beyond a few integers (`factor`, `higher`, `current`, `lower`, running
 * sum). We do **not** build digit arrays or DP tables — **O(1)** auxiliary space.
 *
 * (An equivalent formulation uses recursion / digit DP with memo — same **O(log n)**
 * time but more code; the closed form per position is preferred here.)
 *
 * =============================================================================
 * TIME & SPACE COMPLEXITY
 * =============================================================================
 *
 * Let **d** = number of decimal digits of n (**d = O(log10 n)**).
 * The loop runs once per digit position → **time O(log n)** (base 10 hidden in d).
 * Only constant scalars → **space O(1)**.
 *
 * =============================================================================
 * EDGE CASES
 * =============================================================================
 *
 * - **n == 0:** No positive integers in [1, 0]; answer **0**. Loop `factor <= n`
 *   runs zero times.
 * - **n > 0:** At least digit positions up to MSB are processed.
 * - **Large n:** Python ints handle magnitude; watch **time**, not overflow here.
 *
 * =============================================================================
 * TESTING
 * =============================================================================
 *
 * - **Brute** for n ≤ few 10⁴: stringify each k ∈ [1,n] and count ‘1’s — compare.
 * - Spot checks: n = 13 (expects **6** per classic example), n = 1, n = 9.
 *
 * =============================================================================
 * POSSIBLE IMPROVEMENTS / VARIANTS
 * =============================================================================
 *
 * - **General digit d ∈ [0,9]:** same skeleton with different branch arithmetic —
 *   useful follow-up (“count digit 3”).
 * - **Other bases:** analog formulas with base **B** instead of 10.
 * - **Mathematical rigor in interview:** derive one position’s formula from counting
 *   full **factor**-wide blocks before partial remainder — avoids memorization.
 *
 * =============================================================================
 */

// @lc code=start
class Solution {
    /**
     * Count occurrences of digit '1' in decimal representations of all integers
     * from 1 through n inclusive, in O(log n) time and O(1) extra space.
     */
    public int countDigitOne(int n) {
        if (n <= 0) {
            return 0;
        }

        long total = 0;
        long factor = 1;

        while (factor <= n) {
            long divider = factor * 10;
            long higher = n / divider;
            long current = (n / factor) % 10;
            long lower = n % factor;

            if (current == 0) {
                total += higher * factor;
            } else if (current == 1) {
                total += higher * factor + lower + 1;
            } else {
                total += (higher + 1) * factor;
            }

            factor *= 10;
        }

        return (int) total;
    }
}
// @lc code=end
