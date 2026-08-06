//
// @lc app=leetcode id=1010 lang=python3
//
// [1010] Pairs Of Songs With Total Durations Divisible By 60
//
//
// --- Interview notes (mod 60, complementary remainders, one-pass counting, complexity, edges) ---
//
// Problem
// Count pairs of distinct indices `(i, j)` with `i < j` such that `time[i] + time[j]` is divisible by **60**.
//
// Modular reduction
// Divisibility by 60 depends only on **`time[i] % 60`** and **`time[j] % 60`**. Write **`r = t % 60`** in `{0,…,59}`.
// Need **`(r_i + r_j) % 60 == 0`**, i.e. **`r_j ≡ -r_i (mod 60)`**, i.e. **`r_j ≡ (60 - r_i) mod 60`**.
//
// Why only 60 buckets
// Remainders partition songs into **60** equivalence classes. Pairing is determined solely by `(remainder, remainder)`:
// • **`r = 0`** pairs with **`0`** (`0+0 ≡ 0`).
// • **`r = 30`** pairs with **`30`** (`30+30=60`).
// • **`r ∈ {1,…,29}`** pairs with **`60 - r`** (e.g. `15` with `45`).
//
// One-pass algorithm (ordered pairs `i < j`)
// Sweep left to right. Maintain **`cnt[r]`** = how many **previous** songs have remainder **`r`**.
// For current song with remainder **`r`**, every earlier song with remainder **`need = (60 - r) % 60`** completes a valid pair:
// add **`cnt[need]`** to the answer, then **`cnt[r] += 1`**.
// This counts each unordered pair exactly once when the **later** index is processed.
//
// Why `(60 - r) % 60`**
// Covers **`r = 0`** (`need = 0`) and **`r = 30`** (`need = 30`) uniformly without branching.
//
// Data structure
// **Fixed array of length 60** — **O(1)** extra space; no hash map needed because keys are bounded.
//
// Time complexity **O(n)** — single pass over `time`.
//
// Space complexity **O(1)** — `cnt` size 60 is constant.
//
// Edge cases
// • Many copies of same duration — counting handles duplicates; pairs use **distinct indices** via sequential scan.
// • Duration multiple of 60 — remainder **0**; stacks with other **0** remainders.
//
// Tests (typical)
// • `[30,20,150,100,40]` → **3** (problem example style).
// • `[60,60,60]` → **3** pairs among three zeros mod 60 (`C(3,2)`).
//
// Alternatives
// • Two-pointer after sorting — **O(n log n)**; worse than remainder DP when only divisibility by 60 matters.
// • Nested loops — **O(n²)**; fails constraints.
//
// --- end notes ---
//
// @lc code=start

package leetcode

//
// @lc app=leetcode id=1010 lang=golang
//
// [1010] Pairs Of Songs With Total Durations Divisible By 60
//

// --- Interview notes (mod 60, complementary remainders, one-pass counting, complexity, edges) ---
//
// Problem
// Count pairs of distinct indices `(i, j)` with `i < j` such that `time[i] + time[j]` is divisible by **60**.
//
// Modular reduction
// Divisibility by 60 depends only on **`time[i] % 60`** and **`time[j] % 60`**. Write **`r = t % 60`** in `{0,…,59}`.
// Need **`(r_i + r_j) % 60 == 0`**, i.e. **`r_j ≡ -r_i (mod 60)`**, i.e. **`r_j ≡ (60 - r_i) mod 60`**.
//
// Why only 60 buckets
// Remainders partition songs into **60** equivalence classes. Pairing is determined solely by `(remainder, remainder)`:
// • **`r = 0`** pairs with **`0`** (`0+0 ≡ 0`).
// • **`r = 30`** pairs with **`30`** (`30+30=60`).
// • **`r ∈ {1,…,29}`** pairs with **`60 - r`** (e.g. `15` with `45`).
//
// One-pass algorithm (ordered pairs `i < j`)
// Sweep left to right. Maintain **`cnt[r]`** = how many **previous** songs have remainder **`r`**.
// For current song with remainder **`r`**, every earlier song with remainder **`need = (60 - r) % 60`** completes a valid pair:
// add **`cnt[need]`** to the answer, then **`cnt[r] += 1`**.
// This counts each unordered pair exactly once when the **later** index is processed.
//
// Why `(60 - r) % 60`**
// Covers **`r = 0`** (`need = 0`) and **`r = 30`** (`need = 30`) uniformly without branching.
//
// Data structure
// **Fixed array of length 60** — **O(1)** extra space; no hash map needed because keys are bounded.
//
// Time complexity **O(n)** — single pass over `time`.
//
// Space complexity **O(1)** — `cnt` size 60 is constant.
//
// Edge cases
// • Many copies of same duration — counting handles duplicates; pairs use **distinct indices** via sequential scan.
// • Duration multiple of 60 — remainder **0**; stacks with other **0** remainders.
//
// Tests (typical)
// • `[30,20,150,100,40]` → **3** (problem example style).
// • `[60,60,60]` → **3** pairs among three zeros mod 60 (`C(3,2)`).
//
// Alternatives
// • Two-pointer after sorting — **O(n log n)**; worse than remainder DP when only divisibility by 60 matters.
// • Nested loops — **O(n²)**; fails constraints.
//
// --- end notes ---

// @lc code=start

// NumPairsDivisibleBy601010 counts pairs (i<j) whose total duration is divisible by 60.
func NumPairsDivisibleBy601010(time []int) int {
	var cnt [60]int
	ans := 0
	for _, t := range time {
		r := t % 60
		need := (60 - r) % 60
		ans += cnt[need]
		cnt[r]++
	}
	return ans
}

// @lc code=end

