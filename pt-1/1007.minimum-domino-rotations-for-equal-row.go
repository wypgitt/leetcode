package leetcode

//
// @lc app=leetcode id=1007 lang=golang
//
// [1007] Minimum Domino Rotations For Equal Row
//

// --- Interview notes (two candidates, counting, formula n - max(cnt), complexity, edges) ---
//
// Problem
// `tops[i]` and `bottoms[i]` are the two faces of domino `i` (values in `1..6`). You may swap the two faces on any domino
// (rotation). Minimize the number of rotations so that **either** every `tops[i]` equals the same value **or** every
// `bottoms[i]` equals the same value. Return `-1` if impossible.
//
// Key observation — only two target values are possible
// If after all moves some row is all equal to `x`, then **every** domino must display `x` on at least one face (otherwise
// that domino can never contribute `x` to either row). In particular, domino `0` must contain `x`, so `x ∈ {tops[0],
// bottoms[0]}`. No other value can be the uniform row value — we only need to try **`x = tops[0]`** and **`x = bottoms[0]`**
// (when equal, both checks coincide).
//
// Feasibility for a fixed target `x`
// Scan all indices: if for some `i`, `x ∉ {tops[i], bottoms[i]}`, value `x` is impossible for that row goal → reject `x`.
//
// Minimum rotations for a feasible `x`
// Let `c1` = count of indices with `tops[i] == x`, `c2` = count with `bottoms[i] == x`.
// • To make **top** row all `x`: positions already correct need `0` flips; each other position must have `x` on bottom so we
//   rotate once → **`n - c1`** rotations.
// • To make **bottom** row all `x`: symmetrically **`n - c2`** rotations.
// We may achieve either goal, so **`f(x) = min(n - c1, n - c2) = n - max(c1, c2)`**.
//
// Algorithm
// `answer = min(f(tops[0]), f(bottoms[0]))`, treating impossible candidate as `+∞`. If answer infinite → `-1`.
//
// Why no extra data structures
// Two linear scans (or one helper invoked twice) — **O(1)** beyond input arrays.
//
// Time complexity **O(n)** with `n = len(tops)`.
//
// Space complexity **O(1)** auxiliary (only counters / `inf`).
//
// Edge cases
// • All dominoes already show the same value on top — `c1 == n` → **0** rotations for top row.
// • `tops[0] == bottoms[0]` — still run `f` twice or early dedupe; result unchanged.
//
// Tests (statement)
// • `tops = [2,1,2,4,2,2]`, `bottoms = [5,2,6,2,3,2]` → **2**.
// • `tops = [3,5,1,2,3]`, `bottoms = [3,6,3,3,4]` → **-1**.
//
// Improvements
// • If `tops[0] == bottoms[0]`, evaluate **`f` once**.
// • Values bounded by **6** — could bit-mask count, but unnecessary with **O(n)** scan.
//
// --- end notes ---

// @lc code=start

// MinDominoRotations1007 returns the minimum number of rotations needed so that
// all values in the top row are equal or all values in the bottom row are equal.
func MinDominoRotations1007(tops, bottoms []int) int {
	n := len(tops)

	const inf = int(^uint(0) >> 1) // MaxInt

	minRotationsForTarget := func(x int) int {
		c1, c2 := 0, 0
		for i := 0; i < n; i++ {
			a, b := tops[i], bottoms[i]
			if x != a && x != b {
				return inf
			}
			if a == x {
				c1++
			}
			if b == x {
				c2++
			}
		}
		if c1 > c2 {
			return n - c1
		}
		return n - c2
	}

	ans := minRotationsForTarget(tops[0])
	if v := minRotationsForTarget(bottoms[0]); v < ans {
		ans = v
	}
	if ans == inf {
		return -1
	}
	return ans
}

// @lc code=end

