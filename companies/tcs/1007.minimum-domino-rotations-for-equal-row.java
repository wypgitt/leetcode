/*
 * @lc app=leetcode id=1007 lang=java
 *
 * [1007] Minimum Domino Rotations For Equal Row
 */

/*
 * --- Interview notes (two candidates, counting, formula n - max(cnt), complexity, edges) ---
 *
 * Problem
 * `tops[i]` and `bottoms[i]` are the two faces of domino `i` (values in `1..6`). You may swap the two faces on any domino
 * (rotation). Minimize the number of rotations so that **either** every `tops[i]` equals the same value **or** every
 * `bottoms[i]` equals the same value. Return `-1` if impossible.
 *
 * Key observation — only two target values are possible
 * If after all moves some row is all equal to `x`, then **every** domino must display `x` on at least one face (otherwise
 * that domino can never contribute `x` to either row). In particular, domino `0` must contain `x`, so `x ∈ {tops[0],
 * bottoms[0]}`. No other value can be the uniform row value — we only need to try **`x = tops[0]`** and **`x = bottoms[0]`**
 * (when equal, both checks coincide).
 *
 * Feasibility for a fixed target `x`
 * Scan all indices: if for some `i`, `x ∉ {tops[i], bottoms[i]}`, value `x` is impossible for that row goal → reject `x`.
 *
 * Minimum rotations for a feasible `x`
 * Let `c1` = count of indices with `tops[i] == x`, `c2` = count with `bottoms[i] == x`.
 * • To make **top** row all `x`: positions already correct need `0` flips; each other position must have `x` on bottom so we
 *   rotate once → **`n - c1`** rotations.
 * • To make **bottom** row all `x`: symmetrically **`n - c2`** rotations.
 * We may achieve either goal, so **`f(x) = min(n - c1, n - c2) = n - max(c1, c2)`**.
 *
 * Algorithm
 * `answer = min(f(tops[0]), f(bottoms[0]))`, treating impossible candidate as `+∞`. If answer infinite → `-1`.
 *
 * Why no extra data structures
 * Two linear scans (or one helper invoked twice) — **O(1)** beyond input arrays.
 *
 * Time complexity **O(n)** with `n = len(tops)`.
 *
 * Space complexity **O(1)** auxiliary (only counters / `inf`).
 *
 * Edge cases
 * • All dominoes already show the same value on top — `c1 == n` → **0** rotations for top row.
 * • `tops[0] == bottoms[0]` — still run `f` twice or early dedupe; result unchanged.
 *
 * Tests (statement)
 * • `tops = [2,1,2,4,2,2]`, `bottoms = [5,2,6,2,3,2]` → **2**.
 * • `tops = [3,5,1,2,3]`, `bottoms = [3,6,3,3,4]` → **-1**.
 *
 * Improvements
 * • If `tops[0] == bottoms[0]`, evaluate **`f` once**.
 * • Values bounded by **6** — could bit-mask count, but unnecessary with **O(n)** scan.
 *
 * --- end notes ---
 */

// @lc code=start
class Solution {
    private static final int INF = Integer.MAX_VALUE / 4;

    public int minDominoRotations(int[] tops, int[] bottoms) {
        int n = tops.length;
        int ans = Math.min(minRotationsForTarget(tops, bottoms, tops[0]),
                minRotationsForTarget(tops, bottoms, bottoms[0]));
        return ans >= INF ? -1 : ans;
    }

    private int minRotationsForTarget(int[] tops, int[] bottoms, int x) {
        int n = tops.length;
        int c1 = 0;
        int c2 = 0;
        for (int i = 0; i < n; i++) {
            int a = tops[i];
            int b = bottoms[i];
            if (x != a && x != b) {
                return INF;
            }
            if (a == x) {
                c1++;
            }
            if (b == x) {
                c2++;
            }
        }
        return n - Math.max(c1, c2);
    }
}
// @lc code=end
