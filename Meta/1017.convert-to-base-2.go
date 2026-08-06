//
// @lc app=leetcode id=1017 lang=python3
//
// [1017] Convert To Base -2
//
//
// --- Interview notes (negative radix, digits 0/1, remainder fix, complexity, edges, verification) ---
//
// Problem
// Given integer **`n`**, return its representation in **radix −2** (base −2): digits **`0`** and **`1`** only, no leading
// zeros except the string **`"0"`** for **`n = 0`**.
//
// Mathematical setup
// Value of string **`d_{k-1}…d_0`** in base **`b`** is **`Σ d_i · b^i`**. Here **`b = −2`**, so each step adds **`0`** or
// **`(-2)^i`**.
//
// Repeated division algorithm (same spirit as positive bases)
// Write **`n = q · (−2) + r`** with **`r ∈ {0, 1}`** (desired digits). Integer division **`n // (−2)`** paired with remainder
// **`n % (−2)`** in Python follows **floor** semantics for negative divisors, so **`divmod(n, -2)`** may yield **`r = −1`**.
// Negative remainder is not a legal digit: normalize by **`r ← r + 2`** (still binary alphabet) and **`q ← q + 1`** (borrow /
// carry adjustment) so **`n = q' · (−2) + r'`** with **`r' ∈ {0,1}`**.
//
// Loop
// • **`n == 0`** stop (special-case **`n == 0`** → **`"0"`** before loop).
// • Else **`n, r = divmod(n, -2)`**, **`if r < 0: r += 2; n += 1`**, append **`r`** as least-significant new digit (build
// reversed bit string), **`n`** becomes next quotient.
//
// Output
// Reverse appended digits — MSB last produced corresponds to highest power.
//
// Why not use **`bin()`**
// Built-ins assume nonnegative radix **2**; negative radix needs explicit iterative extraction.
//
// Time complexity **O(log |n|)** — each step strictly reduces **`|n|`** in the relevant sense; number of digits **Θ(log |n|)**
// for **`|n| ≥ 1`**.
//
// Space complexity **O(log |n|)** for the result string (plus **O(1)** arithmetic variables).
//
// Edge cases
// • **`n = 0`** — definition **`"0"`** (loop would otherwise yield empty string).
// • Large **`|n|`** — Python integers unbounded; algorithm only uses **`divmod`**.
//
// Correctness check (interview trick)
// Evaluate **`Σ d_i (−2)^i`** left-to-right or right-to-left to verify against **`n`** on examples.
//
// Tests (sanity)
// • **`n = 2`** → **`"110"`** since **`4 − 2 = 2`**.
// • **`n = 3`** → **`"111"`** ( **`4 − 2 + 1`** ).
//
// Improvements
// • Bit-twiddling variants exist for speed in fixed-width hardware — unnecessary in BigInt Python interviews.
//
// --- end notes ---
//
// @lc code=start

package leetcode

//
// @lc app=leetcode id=1017 lang=golang
//
// [1017] Convert To Base -2
//

// --- Interview notes (negative radix, digits 0/1, remainder fix, complexity, edges, verification) ---
//
// Problem
// Given integer **`n`**, return its representation in **radix −2** (base −2): digits **`0`** and **`1`** only, no leading
// zeros except the string **`"0"`** for **`n = 0`**.
//
// Mathematical setup
// Value of string **`d_{k-1}…d_0`** in base **`b`** is **`Σ d_i · b^i`**. Here **`b = −2`**, so each step adds **`0`** or
// **`(-2)^i`**.
//
// Repeated division algorithm (same spirit as positive bases)
// Write **`n = q · (−2) + r`** with **`r ∈ {0, 1}`** (desired digits). Integer division **`n // (−2)`** paired with remainder
// **`n % (−2)`** in Python follows **floor** semantics for negative divisors, so **`divmod(n, -2)`** may yield **`r = −1`**.
// Negative remainder is not a legal digit: normalize by **`r ← r + 2`** (still binary alphabet) and **`q ← q + 1`** (borrow /
// carry adjustment) so **`n = q' · (−2) + r'`** with **`r' ∈ {0,1}`**.
//
// Loop
// • **`n == 0`** stop (special-case **`n == 0`** → **`"0"`** before loop).
// • Else **`n, r = divmod(n, -2)`**, **`if r < 0: r += 2; n += 1`**, append **`r`** as least-significant new digit (build
// reversed bit string), **`n`** becomes next quotient.
//
// Output
// Reverse appended digits — MSB last produced corresponds to highest power.
//
// Why not use **`bin()`**
// Built-ins assume nonnegative radix **2**; negative radix needs explicit iterative extraction.
//
// Time complexity **O(log |n|)** — each step strictly reduces **`|n|`** in the relevant sense; number of digits **Θ(log |n|)**
// for **`|n| ≥ 1`**.
//
// Space complexity **O(log |n|)** for the result string (plus **O(1)** arithmetic variables).
//
// Edge cases
// • **`n = 0`** — definition **`"0"`** (loop would otherwise yield empty string).
// • Large **`|n|`** — Python integers unbounded; algorithm only uses **`divmod`**.
//
// Correctness check (interview trick)
// Evaluate **`Σ d_i (−2)^i`** left-to-right or right-to-left to verify against **`n`** on examples.
//
// Tests (sanity)
// • **`n = 2`** → **`"110"`** since **`4 − 2 = 2`**.
// • **`n = 3`** → **`"111"`** ( **`4 − 2 + 1`** ).
//
// Improvements
// • Bit-twiddling variants exist for speed in fixed-width hardware — unnecessary in BigInt Python interviews.
//
// --- end notes ---

// @lc code=start

// BaseNeg21017 converts n to its base -2 representation.
func BaseNeg21017(n int) string {
	if n == 0 {
		return "0"
	}
	digits := make([]byte, 0, 32)
	for n != 0 {
		r := n % -2
		n = n / -2
		if r < 0 {
			r += 2
			n += 1
		}
		digits = append(digits, byte('0'+r))
	}

	// reverse
	for i, j := 0, len(digits)-1; i < j; i, j = i+1, j-1 {
		digits[i], digits[j] = digits[j], digits[i]
	}
	return string(digits)
}

// @lc code=end

