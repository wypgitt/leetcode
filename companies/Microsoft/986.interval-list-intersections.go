package leetcode

//
// @lc app=leetcode id=986 lang=golang
//
// [986] Interval List Intersections
//

// --- Interview notes (two sorted lists, intersection formula, advance rule, complexity, edges) ---
//
// Problem
// **`firstList`** and **`secondList`** are **sorted**, pairwise **non-overlapping**, closed intervals **`[start, end]`**.
// Return **all non-empty intersections** between some interval from **`firstList`** and some interval from **`secondList`**,
// as a sorted list (natural merge order from the linear scan).
//
// Geometry of one pair
// For **`A = [a0, a1]`** and **`B = [b0, b1]`**, the overlap is **`[max(a0, b0), min(a1, b1)]`**. It is **non-empty** iff
// **`max(a0, b0) ≤ min(a1, b1)`** (closed intervals).
//
// Why two pointers (merge-intersect pattern)
// Like merging sorted arrays, at each step only **current** **`firstList[i]`** and **`secondList[j]`** can produce a new intersection
// involving “the next” uncovered overlap — earlier intervals are already finished because lists are sorted by start time.
//
// Advance rule (discard the interval that ends first)
// After recording an overlap (if any), move **`i`** if **`firstList[i]` ends before **`secondList[j]`**, else move **`j`**.
// The interval that finishes **earlier** cannot intersect **future** intervals from the other list beyond that cutoff — only the
// longer-span partner might still overlap the **next** interval on the other side.
// When **`a1 == b1`**, advancing **`j`** (or symmetrically **`i`**) is standard; both intervals are exhausted at the same
// coordinate for overlap purposes with each other (next pair picks up fresh intervals).
//
// Data structures
// Output **`res`** list only — **O(k)** for **`k`** intersection segments. No heaps or segment trees needed.
//
// Time complexity **O(m + n)`** — each pointer moves strictly forward, **`m = len(firstList)`**, **`n = len(secondList)`**.
//
// Space complexity **O(1)** auxiliary excluding the answer list (**O(k)** output).
//
// Edge cases
// • Either list **empty** → **no** intersections → **`[]`**.
// • Single-point overlap **`[5,5]`** — still valid closed interval if **`max ≤ min`** with equality.
//
// Tests (LeetCode Example 1)
// • **`firstList = [[0,2],[5,10],[13,23],[24,25]]`**, **`secondList = [[1,5],[8,12],[15,24],[25,26]]`** → six overlapping segments
//   **`[[1,2],[5,5],[8,10],[15,23],[24,24],[25,25]]`**.
//
// Improvements
// • If intervals were half-open **`[l, r)`**, intersection formula adjusts endpoints accordingly — same pointer skeleton.
//
// --- end notes ---

// @lc code=start

// IntervalIntersection986 returns all intersections between two sorted, disjoint interval lists.
func IntervalIntersection986(firstList [][]int, secondList [][]int) [][]int {
	i, j := 0, 0
	out := make([][]int, 0)
	for i < len(firstList) && j < len(secondList) {
		a0, a1 := firstList[i][0], firstList[i][1]
		b0, b1 := secondList[j][0], secondList[j][1]
		lo := a0
		if b0 > lo {
			lo = b0
		}
		hi := a1
		if b1 < hi {
			hi = b1
		}
		if lo <= hi {
			out = append(out, []int{lo, hi})
		}
		if a1 < b1 {
			i++
		} else {
			j++
		}
	}
	return out
}

// @lc code=end

