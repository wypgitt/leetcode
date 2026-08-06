//
// @lc app=leetcode id=1014 lang=python3
//
// [1014] Best Sightseeing Pair
//
//
// --- Interview notes (algebraic split, one-pass “best left”, complexity, edges, alternatives) ---
//
// Problem
// Integer array `values` (sightseeing values). For indices **`i < j`**, sightseeing score is
// **`values[i] + values[j] + i - j`**. Return the **maximum** score over all ordered pairs **`i < j`**.
//
// Reformulation (why this isn’t O(n²))
// Split the expression:
// **`values[i] + values[j] + i - j = (values[i] + i) + (values[j] - j)`**.
// For a fixed **`j`**, **`(values[j] - j)`** is constant, so we should pair **`j`** with the index **`i < j`** that **maximizes**
// **`values[i] + i`**. No need to scan all previous **`i`** each time if we maintain the running maximum.
//
// Algorithm
// • **`best`** = maximum **`values[i] + i`** seen so far for **`i`** strictly to the left of the current index.
// • Scan **`j`** from **`1`** to **`n - 1`**. Update **`answer = max(answer, best + values[j] - j)`**, then
//   **`best = max(best, values[j] + j)`** so future positions can use **`j`** as a left endpoint.
// • Initialize **`best = values[0] + 0`** (only valid left index before the loop).
//
// Correctness sketch
// Every pair **`(i, j)`** with **`i < j`** is considered exactly when the outer index reaches **`j`**, with **`best`** equal to
// **`max_{k < j}(values[k] + k)`** only if we update **`best`** after processing each index — we update **`best`** using **`j`**
// **after** scoring pairs ending at **`j`**, so pairs **`(j, *)`** for larger right endpoints use **`j`** on the left — correct.
//
// Data structures
// Two scalars (**`best`**, **`answer`**) — **O(1)** extra space; input array read-only.
//
// Time complexity **O(n)** — single left-to-right pass.
//
// Space complexity **O(1)** auxiliary.
//
// Edge cases
// • **`n == 2`** — only one pair; algorithm returns **`values[0] + values[1] + 0 - 1`**.
// • Non-increasing **`values`** — still linear; **`best`** may stay at the first peak for score.
//
// Tests (statement / sanity)
// • `values = [8,1,5,2,6]` → **11** (pair `(0,2)`: `8 + 5 + 0 - 2`).
//
// Alternatives
// • Brute force **O(n²)** — correct but fails larger constraints.
// • Precompute prefix max of **`values[i]+i`** in an array — **O(n)** time but **O(n)** space; streaming **`best`** is strictly
//   better on memory.
//
// --- end notes ---
//
// @lc code=start

package leetcode

//
// @lc app=leetcode id=1014 lang=golang
//
// [1014] Best Sightseeing Pair
//

// --- Interview notes (algebraic split, one-pass “best left”, complexity, edges, alternatives) ---
//
// Problem
// Integer array `values` (sightseeing values). For indices **`i < j`**, sightseeing score is
// **`values[i] + values[j] + i - j`**. Return the **maximum** score over all ordered pairs **`i < j`**.
//
// Reformulation (why this isn’t O(n²))
// Split the expression:
// **`values[i] + values[j] + i - j = (values[i] + i) + (values[j] - j)`**.
// For a fixed **`j`**, **`(values[j] - j)`** is constant, so we should pair **`j`** with the index **`i < j`** that **maximizes**
// **`values[i] + i`**. No need to scan all previous **`i`** each time if we maintain the running maximum.
//
// Algorithm
// • **`best`** = maximum **`values[i] + i`** seen so far for **`i`** strictly to the left of the current index.
// • Scan **`j`** from **`1`** to **`n - 1`**. Update **`answer = max(answer, best + values[j] - j)`**, then
//   **`best = max(best, values[j] + j)`** so future positions can use **`j`** as a left endpoint.
// • Initialize **`best = values[0] + 0`** (only valid left index before the loop).
//
// Correctness sketch
// Every pair **`(i, j)`** with **`i < j`** is considered exactly when the outer index reaches **`j`**, with **`best`** equal to
// **`max_{k < j}(values[k] + k)`** only if we update **`best`** after processing each index — we update **`best`** using **`j`**
// **after** scoring pairs ending at **`j`**, so pairs **`(j, *)`** for larger right endpoints use **`j`** on the left — correct.
//
// Data structures
// Two scalars (**`best`**, **`answer`**) — **O(1)** extra space; input array read-only.
//
// Time complexity **O(n)** — single left-to-right pass.
//
// Space complexity **O(1)** auxiliary.
//
// Edge cases
// • **`n == 2`** — only one pair; algorithm returns **`values[0] + values[1] + 0 - 1`**.
// • Non-increasing **`values`** — still linear; **`best`** may stay at the first peak for score.
//
// Tests (statement / sanity)
// • `values = [8,1,5,2,6]` → **11** (pair `(0,2)`: `8 + 5 + 0 - 2`).
//
// Alternatives
// • Brute force **O(n²)** — correct but fails larger constraints.
// • Precompute prefix max of **`values[i]+i`** in an array — **O(n)** time but **O(n)** space; streaming **`best`** is strictly
//   better on memory.
//
// --- end notes ---

// @lc code=start

// MaxScoreSightseeingPair1014 returns the maximum score values[i] + values[j] + i - j for i < j.
func MaxScoreSightseeingPair1014(values []int) int {
	best := values[0] // values[0] + 0
	ans := 0
	for j := 1; j < len(values); j++ {
		score := best + values[j] - j
		if score > ans {
			ans = score
		}
		if v := values[j] + j; v > best {
			best = v
		}
	}
	return ans
}

// @lc code=end

