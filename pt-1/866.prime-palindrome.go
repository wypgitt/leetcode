package leetcode

import "strconv"

//
// @lc app=leetcode id=866 lang=golang
//
// [866] Prime Palindrome
//

// =============================================================================
// INTERVIEW: ELEVATOR PITCH (~30 seconds)
// =============================================================================
//
// "We need the smallest prime ≥ n that is a palindrome. Scanning every integer is
// slow; instead generate **only palindromes** in increasing order by length. A classic
// number-theory fact: every **even-length** palindrome (except 11) is divisible by **11**,
// so no even-digit prime palindrome beyond 11 — we generate **odd-length** palindromes
// by mirroring a left half. Trial divide for primality on each candidate — digit count
// stays small under problem bounds."
//
// =============================================================================
// PROBLEM (PRECISE)
// =============================================================================
//
// Given integer **`n`**, return the **smallest** integer **`x ≥ n`** such that **`x`** is
// both **prime** and a **decimal palindrome** (reads same forwards/backwards).
//
// =============================================================================
// WHY NOT BRUTE-FORCE `x = n, n+1, …` FOR LARGE `n`
// =============================================================================
//
// Primality + palindrome check per integer is cheap, but **gaps** between palindromes
// grow quickly — worst-case attempts approach **`10⁸`** regime from constraints. Generating
// palindromes **directly** skips almost all integers.
//
// =============================================================================
// STRUCTURAL FACT — EVEN-LENGTH PALINDROMES AND 11 (EXCEPT 11)
// =============================================================================
//
// Write a **`2k`-digit** palindrome **`P`** in decimal. Alternating-sum divisibility rule
// for **11** implies **`11 | P`** for **`k ≥ 2`** (standard digit-pattern proof). So **no**
// prime palindrome has **even** length **≥ 4**. The only **even-length** prime palindrome
// is **`11`** (handled as a **small case**).
//
// Therefore for **`n > 11`**, candidates may be restricted to **odd** digit lengths **≥ 3**
// (and single-digit primes already covered by early returns if **`n` ≤ 7**).
//
// =============================================================================
// GENERATING ODD-LENGTH PALINDROMES
// =============================================================================
//
// An odd-length palindrome is determined by its **first `(L+1)//2` digits** — call that
// string **`s`**. The full palindrome is:
//
//       **`int(s + reverse(s[:-1]))`** in Go: mirror `s` excluding last rune, reversed
//
// Example: **`s = "123"`** → **`"123" + "21"`** = **`"12321"`**.
//
// For fixed **`L`** odd, iterate **`s`** numerically from **`10^{(L-1)/2}`** to **`10^{(L+1)/2}-1`**
// (all valid left halves of length **`(L+1)//2`**).
//
// =============================================================================
// PRIMALITY — TRIAL DIVISION
// =============================================================================
//
// For integers up to about **`10⁹`**, trial division up to **`√x`** with **2** then odd
// steps is sufficient here (constraints modest). **Miller–Rabin** is optional overhead
// unless ranges explode.
//
// =============================================================================
// DATA STRUCTURES
// =============================================================================
//
// **Scalars and strings only** — no graphs, heaps, or arrays besides loop counters.
// Building **`s`** as string avoids manual digit reversal arithmetic bugs.
//
// =============================================================================
// TIME & SPACE COMPLEXITY
// =============================================================================
//
// Let **`P`** be the number of palindromes tried until the answer (problem-dependent).
// Each candidate: **`O(√x)`** trial division, **`O(1)`** extra space aside from **`√x`**
// iteration.
//
// Palindromes generated grow slowly vs scanning all integers — overall comfortably within
// limits for **`n ≤ 10⁸`** style bounds.
//
// =============================================================================
// EDGE CASES
// =============================================================================
//
// • **`n ≤ 2`** → **`2`** (only even prime).
// • **`n ∈ {3,4,5}`** → **`5`** or **`7`** per chain.
// • **`n ∈ {6,7,8,9,10}`** → **`7`** or **`11`** as applicable.
// • **`n = 11`** → **`11`**.
// • **`n > 11`** → search odd-length palindromes only ( **`11`** already excluded by **`n`** ).
//
// =============================================================================
// TESTING (SANITY)
// =============================================================================
//
// • **`n = 6`** → **`7`**.
// • **`n = 12` or `13`** → **`101`** (first prime palindrome **`≥ 12`** is **`101`**).
// • **`n = 998`** → **`10301`** (scan jumps past non-prime **`999`**, even-length palindromes
//   divisible by **`11`**, etc.).
// • Cross-check: brute scan small **`n`** with naive prime test for **`n ≤ 10⁴`**.
//
// =============================================================================
// IMPROVEMENTS / VARIANTS
// =============================================================================
//
// • **Next-permutation style** palindrome walk — rarely needed.
// • **Sieve** precomputation — only wins if many queries; single **`n`** here.
//
// =============================================================================

// @lc code=start

// PrimePalindrome866 returns the smallest prime palindrome >= n.
//
// Small primes handled explicitly. For n > 11, only odd-length palindromes are
// candidates (even-length palindromes with >= 4 digits are divisible by 11).
func PrimePalindrome866(n int) int {
	isPrime := func(x int) bool {
		if x < 2 {
			return false
		}
		if x%2 == 0 {
			return x == 2
		}
		limit := intSqrt(x) + 1
		for d := 3; d < limit; d += 2 {
			if x%d == 0 {
				return false
			}
		}
		return true
	}

	if n <= 2 {
		return 2
	}
	if n <= 3 {
		return 3
	}
	if n <= 5 {
		return 5
	}
	if n <= 7 {
		return 7
	}
	if n <= 11 {
		return 11
	}

	// Odd total length L only (even-length palindromes with L >= 4 are multiples of 11).
	L := len(strconv.Itoa(n))
	if L%2 == 0 {
		L++
	}

	for {
		halfLo := pow10((L - 1) / 2)
		halfHi := pow10((L + 1) / 2)
		for half := halfLo; half < halfHi; half++ {
			s := strconv.Itoa(half)
			// cand = int(s + s[:-1][::-1])
			cand, _ := strconv.Atoi(s + reverseString(s[:len(s)-1]))
			if cand >= n && isPrime(cand) {
				return cand
			}
		}
		L += 2
	}
}

func intSqrt(x int) int {
	// integer sqrt for trial division bound
	if x < 0 {
		return 0
	}
	r := x
	for r*r > x {
		r = (r + x/r) / 2
	}
	return r
}

func pow10(k int) int {
	p := 1
	for i := 0; i < k; i++ {
		p *= 10
	}
	return p
}

func reverseString(s string) string {
	r := []rune(s)
	for i, j := 0, len(r)-1; i < j; i, j = i+1, j-1 {
		r[i], r[j] = r[j], r[i]
	}
	return string(r)
}

// @lc code=end
