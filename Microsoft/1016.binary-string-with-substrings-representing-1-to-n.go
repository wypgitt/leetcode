//
// @lc app=leetcode id=1016 lang=python3
//
// [1016] Binary String With Substrings Representing 1 To N
//

// --- Interview notes (substring check, halving trick, prefix lemma, complexity, edges) ---
//
// Problem
// Given a binary string **`s`** and positive integer **`n`**, return **`True`** iff for **every** integer **`x` in
// `1..n`**, the binary form of **`x` without the `0b` prefix and without leading zeros** (e.g. `1, 10, 11, …`) appears
// as a **contiguous substring** of **`s`**.
//
// Naive approach
// For each **`x` from 1 to `n`**, test **`bin(x)[2:]` in s** — correct, **O(n · |s|)** substring scans worst-case (Python `in`
// uses efficient search but linear in **`|s|`** per check).
//
// Optimization — only verify **`⌊n/2⌋ + 1 … n`**
// Lemma: For **`k ≥ 1`**, **`bin(2k)`** equals **`bin(k)` with one extra `'0'` appended at the right** (multiply by two ⇔
// left shift in binary). Hence **`bin(k)` is a prefix of `bin(2k)`** (same bits before that trailing zero).
// Therefore **`bin(2k)` contains `bin(k)` as a substring** (prefix is a substring). So if **`s`** contains **`bin(2k)`** and
// **`2k ≤ n`**, then **`s`** necessarily contains **`bin(k)`** as well.
// • Any **`k ≤ ⌊n/2⌋`** satisfies **`2k ≤ n`**. So covering every **`x` in `[⌊n/2⌋ + 1, n]`** inductively forces coverage of
// **`1 … ⌊n/2⌋`** via repeated halving / prefix containment chains.
// Thus it suffices to check **`x ∈ {⌊n/2⌋ + 1, …, n}`** only — **roughly half as many** substring tests.
//
// Algorithm
// For **`i`** from **`n // 2 + 1`** to **`n`**, if **`bin(i)[2:]`** not in **`s`**, return **`False`**. Otherwise return **`True`**.
//
// Data structures
// No extra structures — only Python string membership (substring search). Optional: build a **suffix automaton** or
// **rolling-hash set** of substrings for **`O(1)`** queries — overkill for typical **`|s|, n`** bounds.
//
// Time complexity **O((n - n/2) · |s|) = O(n · |s|)** worst-case for substring checks; constant-factor improved vs full **`1..n`**.
//
// Space complexity **O(1)** beyond input strings (binary representation strings are **O(log n)** characters each).
//
// Edge cases
// • **`n == 1`** — loop **`range(1, 2)`** checks **`bin(1) == "1"`** once.
// • **`s`** very short — fails quickly if a required pattern cannot fit.
//
// Tests (sanity)
// • **`s = "0110"`, `n = 3`** — contains **`1`, `10`, `11`** → **`True`** (verify manually).
// • **`s = "0110"`, `n = 4`** — need **`100`** for **`4`** → **`False`** if **`100`** missing.
//
// Improvements
// • **Bit-length batching**: group checks by pattern length and use a hash set of all substrings of **`s`** of length **`L`**
//   — **O(|s|)** per length — useful if **`n`** is huge (not usually needed here).
//
// --- end notes ---
//
// @lc code=start

package leetcode

import (
	"strconv"
	"strings"
)

//
// @lc app=leetcode id=1016 lang=golang
//
// [1016] Binary String With Substrings Representing 1 To N
//

// --- Interview notes (substring check, halving trick, prefix lemma, complexity, edges) ---
//
// Problem
// Given a binary string **`s`** and positive integer **`n`**, return **`True`** iff for **every** integer **`x` in
// `1..n`**, the binary form of **`x` without the `0b` prefix and without leading zeros** (e.g. `1, 10, 11, …`) appears
// as a **contiguous substring** of **`s`**.
//
// Naive approach
// For each **`x` from 1 to `n`**, test **`bin(x)[2:]` in s** — correct, **O(n · |s|)** substring scans worst-case (Python `in`
// uses efficient search but linear in **`|s|`** per check).
//
// Optimization — only verify **`⌊n/2⌋ + 1 … n`**
// Lemma: For **`k ≥ 1`**, **`bin(2k)`** equals **`bin(k)` with one extra `'0'` appended at the right** (multiply by two ⇔
// left shift in binary). Hence **`bin(k)` is a prefix of `bin(2k)`** (same bits before that trailing zero).
// Therefore **`bin(2k)` contains `bin(k)` as a substring** (prefix is a substring). So if **`s`** contains **`bin(2k)`** and
// **`2k ≤ n`**, then **`s`** necessarily contains **`bin(k)`** as well.
// • Any **`k ≤ ⌊n/2⌋`** satisfies **`2k ≤ n`**. So covering every **`x` in `[⌊n/2⌋ + 1, n]`** inductively forces coverage of
// **`1 … ⌊n/2⌋`** via repeated halving / prefix containment chains.
// Thus it suffices to check **`x ∈ {⌊n/2⌋ + 1, …, n}`** only — **roughly half as many** substring tests.
//
// Algorithm
// For **`i`** from **`n // 2 + 1`** to **`n`**, if **`bin(i)[2:]`** not in **`s`**, return **`False`**. Otherwise return **`True`**.
//
// Data structures
// No extra structures — only Python string membership (substring search). Optional: build a **suffix automaton** or
// **rolling-hash set** of substrings for **`O(1)`** queries — overkill for typical **`|s|, n`** bounds.
//
// Time complexity **O((n - n/2) · |s|) = O(n · |s|)** worst-case for substring checks; constant-factor improved vs full **`1..n`**.
//
// Space complexity **O(1)** beyond input strings (binary representation strings are **O(log n)** characters each).
//
// Edge cases
// • **`n == 1`** — loop **`range(1, 2)`** checks **`bin(1) == "1"`** once.
// • **`s`** very short — fails quickly if a required pattern cannot fit.
//
// Tests (sanity)
// • **`s = "0110"`, `n = 3`** — contains **`1`, `10`, `11`** → **`True`** (verify manually).
// • **`s = "0110"`, `n = 4`** — need **`100`** for **`4`** → **`False`** if **`100`** missing.
//
// Improvements
// • **Bit-length batching**: group checks by pattern length and use a hash set of all substrings of **`s`** of length **`L`**
//   — **O(|s|)** per length — useful if **`n`** is huge (not usually needed here).
//
// --- end notes ---

// @lc code=start

// QueryString1016 reports whether s contains the binary representation of every integer in [1..n] as a substring.
func QueryString1016(s string, n int) bool {
	for x := n/2 + 1; x <= n; x++ {
		b := strconv.FormatInt(int64(x), 2)
		if !strings.Contains(s, b) {
			return false
		}
	}
	return true
}

// @lc code=end

