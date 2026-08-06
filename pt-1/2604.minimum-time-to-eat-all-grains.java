/*
 * @lc app=leetcode id=2604 lang=java
 *
 * [2604] Minimum Time to Eat All Grains
 */

/*
 * --- Interview notes: problem, algorithm, correctness, complexity, tests, edges ---
 *
 * Problem restatement
 * - n hens and m grains lie on a 1-D line (integer positions).
 * - Eating takes zero time once a hen reaches a grain.
 * - Each second, each hen may move 1 unit left OR right (hens move in parallel).
 * - Any hen may eat multiple grains. Act optimally to minimize the completion time: the
 *   smallest T such that every grain has been eaten by time T.
 *
 * Why binary search on T?
 * - Monotonicity: if all grains can be finished within T seconds, they can also finish within
 *   any T' >= T (just wait longer). So feasibility F(T) is monotone in T.
 * - We seek min T with F(T)=true -> classic binary search on the answer.
 *
 * Why sort both arrays?
 * - Process hens left-to-right after sorting; assign each hen the next uneaten grains from the
 *   left in sorted grain order. Any optimal assignment can be reordered to this form: if two
 *   hens h1 < h2 would eat grains g1 < g2 but h1 eats g2 and h2 eats g1, swapping assignments
 *   does not increase needed time (interval scheduling on a line). So greedy by sorted order is safe.
 *
 * Feasibility check check(T) — two-pointer greedy
 * - j = leftmost uneaten grain index.
 * - For each hen at position x, look at y = grains[j].
 *
 * Case A — leftmost grain is at or to the left of the hen (y <= x)
 * - The hen must at least reach y; distance d = x - y. If d > T, impossible (return false).
 * - First eat every grain still <= x without passing x (already on the way when walking left from x
 *   toward y); advance j while grains[j] <= x.
 * - Remaining grains (if any) lie strictly to the right of x. Optional strategy for the hen:
 *     go left to y (cost d), then walk right eating further grains; OR walk right first within budget.
 *   The editorial inequality for the next grain at grains[j] is:
 *       min(d, grains[j] - x) + (grains[j] - y) <= T
 *   Interpretation: min(d, grains[j]-x) is the extra horizontal movement needed beyond closing to x
 *   before traveling from y to grains[j] along the line (short proof matches optimal zigzag on a segment).
 *   While this holds, consume grains and advance j.
 *
 * Case B — leftmost grain is strictly to the right of the hen (y > x)
 * - Only moving right matters until those grains are eaten: accept grain j while grains[j] - x <= T.
 *
 * After all hens, success iff j == m (every grain assigned).
 *
 * Binary search bounds
 * - lo = 0; hi can be an upper bound on the answer. Safe choices: spread of positions, e.g.
 *   abs(hens[0]-grains[0]) + (grains[m-1]-grains[0]) from the line span, or 2e9. hi must be >= answer.
 * - Search invariant: first feasible time using standard lower_bound style (while lo < hi, mid,
 *   shrink hi if check(mid) else lo = mid+1).
 *
 * Time complexity
 * - Sorting: O(n log n + m log m).
 * - Each check(T): j only moves forward -> O(n + m) per probe.
 * - Binary search on T: O(log U) probes where U is hi (coordinate magnitude ~1e9 -> ~31 iterations).
 * - Total: O((n+m) log U + n log n + m log m), dominated by sorting and feasibility checks.
 *
 * Space complexity
 * - O(1) extra besides input arrays (sorting may be O(log n) stack for sort); sort is in-place.
 *
 * Data structures
 * - Primitive arrays + indices (two pointers). No extra containers required beyond sorting.
 *
 * Edge cases
 * - One hen eats all grains: single hen loop must cover entire grains array.
 * - Grains all on one side of every hen: case B only for early hens.
 * - Equal positions: d = 0; case A degrades cleanly.
 *
 * Tests (examples)
 * - hens=[3,6,7], grains=[2,4,7,9] -> 2 (assign as in statement).
 * - hens=[4,6,109,111,213,215], grains=[5,110,214] -> 1.
 *
 * Improvements / variants
 * - If hi bound is tight, wrong hi causes WA; a conservative hi = 2_000_000_000 is acceptable under constraints.
 * - bisect could be written with Long if hi exceeds int when combining distances (not needed here with given bounds).
 *
 * Common pitfalls
 * - Unsorted input (must sort).
 * - Off-by-one in binary search (ensure minimum feasible T).
 * - In case A, forgetting the second while loop for grains to the right of x with the min(d, ...) rule.
 * --- end notes ---
 */

import java.util.Arrays;

// @lc code=start
class Solution {
    public int minimumTime(int[] hens, int[] grains) {
        Arrays.sort(hens);
        Arrays.sort(grains);
        int m = grains.length;
        int hi = Math.abs(hens[0] - grains[0]) + grains[m - 1] - grains[0];
        int lo = 0;
        while (lo < hi) {
            int mid = (lo + hi) >>> 1;
            if (check(mid, hens, grains)) {
                hi = mid;
            } else {
                lo = mid + 1;
            }
        }
        return lo;
    }

    /** Returns true iff all grains can be eaten within t seconds (sorted inputs). */
    private boolean check(int t, int[] hens, int[] grains) {
        int m = grains.length;
        int j = 0;
        for (int x : hens) {
            if (j == m) {
                return true;
            }
            int y = grains[j];
            if (y <= x) {
                int d = x - y;
                if (d > t) {
                    return false;
                }
                while (j < m && grains[j] <= x) {
                    j++;
                }
                while (j < m && Math.min(d, grains[j] - x) + grains[j] - y <= t) {
                    j++;
                }
            } else {
                while (j < m && grains[j] - x <= t) {
                    j++;
                }
            }
        }
        return j == m;
    }
}
// @lc code=end
