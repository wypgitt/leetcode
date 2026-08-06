//
// @lc app=leetcode id=907 lang=java
//
// [907] Sum of Subarray Minimums
//

// =============================================================================
// INTERVIEW: ELEVATOR PITCH (~30 seconds)
// =============================================================================
//
// "Summing min over all subarrays naively is O(n³). Flip the question: each index i
// contributes arr[i] times how many subarrays **choose arr[i] as their minimum**
// (with a fixed tie-break on duplicates). Those counts factor into left × right choices.
// Two monotone-stack scans find the nearest smaller boundary on each side — O(n)
// total. Multiply, sum, modulo 10⁹+7."
//
// =============================================================================
// PROBLEM (PRECISE)
// =============================================================================
//
// For every contiguous subarray of `arr`, take its minimum. Return the **sum** of
// those minima over all subarrays, modulo **10⁹ + 7**.
//
// =============================================================================
// CONTRIBUTION OF EACH INDEX — WHY arr[i] × left × RIGHT
// =============================================================================
//
// Fix index `i`. Consider subarrays **that include position `i`** and whose
// **minimum value equals `arr[i]`** under this **tie-breaking rule**:
//
//   Among equal values in a subarray, we attribute the subarray to the **leftmost**
//   occurrence of that minimum (equivalently: previous strictly smaller on the left,
//   next smaller-or-equal on the right — see stack inequalities below).
//
// Then such a subarray `[L, R]` must satisfy:
//   • `L ≤ i ≤ R`
//   • every element in `[L, i]` is **≥ arr[i]** (else min would be smaller left),
//     and strictly **>** on `[L, i)` relative to tie-breaking — enforced by stopping
//     `L` right after the previous index with value **< arr[i]**.
//   • symmetric condition on the right up to the next index with value **≤ arr[i]**.
//
// Count of valid `L` choices × count of valid `R` choices gives **independent**
// rectangle counting → contribution **`arr[i] × left_count × right_count`**.
//
// =============================================================================
// MONOTONE STACK — DISTANCES TO PREVIOUS / NEXT "BOUNDARY"
// =============================================================================
//
// **Left scan (increasing stack, popping strictly larger tops):**
//
//   While `arr[stack.top] > arr[i]`, pop.
//   Then either stack empty → previous `<` is "before 0" → `left_count = i + 1`,
//   or top is index `p` with `arr[p] < arr[i]` → valid starts are `p+1 … i`,
//   giving **`left_count = i - p`**.
//
// **Right scan (decreasing index, popping strictly larger OR EQUAL tops):**
//
//   While `arr[stack.top] >= arr[i]`, pop (note **`>=`**).
//   Next boundary `q` has `arr[q] ≤ arr[i]` so min shifts right on ties — avoids
//   double-counting duplicates symmetrically with strict `>` on the left.
//
//   `right_count = q - i`, or **`n - i`** if none.
//
// Together each subarray is assigned to exactly one "responsible" index among equals.
//
// =============================================================================
// DATA STRUCTURES
// =============================================================================
//
// • **Monotonic stack** of indices — `O(n)` worst-case size; each index pushed/popped
//   **once per direction** → **amortized O(n)** per scan.
// • **Arrays `left`, `right`** — `O(n)` space for boundary distances.
//
// No heaps, segment trees, or DP tables required for the standard solution.
//
// =============================================================================
// TIME & SPACE COMPLEXITY
// =============================================================================
//
// • Two passes × amortized linear stack work → **O(n)** time.
// • **O(n)** auxiliary space for `left`, `right`, and stack.
//
// =============================================================================
// EDGE CASES
// =============================================================================
//
// • **`n == 1`** — single subarray; answer `arr[0]`.
// • **Strictly increasing** — each element is min only in subarrays ending/starting at it;
//   stack logic still applies.
// • **Duplicates** — **`>` vs `>=`** pairing is **essential**; swapping breaks correctness.
// • **Modulo** — apply `% MOD` on the accumulator (Python big ints safe; still mod each
//   term or final sum per problem).
//
// =============================================================================
// TESTING (MANUAL / UNIT)
// =============================================================================
//
// • **Tiny brute force:** enumerate all `O(n²)` subarrays, min each in `O(n)` → `O(n³)`
//   only for `n ≤ 8` random arrays vs stack formula.
// • **Known:** `[3,1,2,4]` sums to **17** (walkthrough all 10 subarrays).
//
// =============================================================================
// IMPROVEMENTS / VARIANTS
// =============================================================================
//
// • Single-stack variants exist but two-pass is clearest in interviews.
// • **Sum of subarray maximums** — symmetric with decreasing stacks / flipped inequalities.
//
// =============================================================================

// @lc code=start

import java.util.ArrayDeque;
import java.util.Deque;

class Solution {

    private static final int MOD = 1_000_000_007;

    /**
     * Sum of min(subarray) over all contiguous subarrays.
     * <p>
     * For each i, count subarrays where arr[i] is the minimum under duplicate
     * tie-breaking (strictly smaller on left, smaller-or-equal on right).
     * Contribution arr[i] * left[i] * right[i]; monotone stacks count boundaries.
     */
    public int sumSubarrayMins(int[] arr) {
        int n = arr.length;
        int[] left = new int[n];
        int[] right = new int[n];

        Deque<Integer> stack = new ArrayDeque<>();
        for (int i = 0; i < n; i++) {
            while (!stack.isEmpty() && arr[stack.peek()] > arr[i]) {
                stack.pop();
            }
            if (!stack.isEmpty()) {
                left[i] = i - stack.peek();
            } else {
                left[i] = i + 1;
            }
            stack.push(i);
        }

        stack.clear();
        for (int i = n - 1; i >= 0; i--) {
            while (!stack.isEmpty() && arr[stack.peek()] >= arr[i]) {
                stack.pop();
            }
            if (!stack.isEmpty()) {
                right[i] = stack.peek() - i;
            } else {
                right[i] = n - i;
            }
            stack.push(i);
        }

        long ans = 0;
        for (int i = 0; i < n; i++) {
            ans = (ans + (long) arr[i] * left[i] * right[i]) % MOD;
        }
        return (int) ans;
    }
}

// @lc code=end
