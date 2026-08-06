package leetcode

//
// LeetCode 201 — Bitwise AND of Numbers Range
//
// =============================================================================
// PROBLEM (precise)
// =============================================================================
//
// Given integers left <= right, compute:
//
//   AND_{x=left}^{right} x
//
// i.e. bitwise AND of every integer in the inclusive range [left, right].
//
// =============================================================================
// WHY NAIVE FAILS
// =============================================================================
//
// Iterating x from left to right and updating ans &= x is correct but takes
// **O(right - left)** time — unacceptable when the interval spans billions (LeetCode
// constraints allow large 31-bit values).
//
// We need **O(log U)** time at worst (U ~ max(|left|, |right|)), using structure of
// binary representation — **no auxiliary arrays required**.
//
// =============================================================================
// KEY OBSERVATION (common prefix / stripping unstable suffix bits)
// =============================================================================
//
// Write left and right in binary. For any bit position k (counting from LSB = 0):
//
// - If left and right **disagree** at bit k (one has 0, the other 1), then as we
//   enumerate **all** integers from left to right, that bit position takes **both**
//   values 0 and 1 across the range (the range crosses a boundary where that bit
//   flips). The bitwise AND across **all** numbers therefore forces that bit to **0**.
//
// - Bits where left and right **agree** might still become 0 if intermediate values
//   flip them — but the **high-order bits that are identical** for **both** endpoints
//   and define the same **prefix** before the first differing position are **stable**:
//   they stay 1 for **every** number in [left, right]. Those bits survive the AND.
//
// Equivalently: the answer is the **shared binary prefix** of left and right,
// **zero-padded** on the right up to the word length — i.e. **clear every bit to the
// right of the most significant bit where left and right differ**.
//
// =============================================================================
// ALGORITHM A (implemented): right-shift until equal
// =============================================================================
//
// Repeat:
//   left  >>= 1
//   right >>= 1
//   shift += 1
// until left == right.
//
// Then return left << shift.
//
// Interpretation: each right-shift drops the **least significant** bit from both
// endpoints — exactly removing bits that cannot be common to the entire range’s AND.
// When the truncated values become equal, we have isolated the **common prefix**;
// shifting left restores it.
//
// **Time:** O(log right) bit operations — at most ~31 iterations for 32-bit positives.
// **Space:** O(1).
//
// =============================================================================
// ALGORITHM B (alternative — see comments after code): clear low bits of `right`
// =============================================================================
//
// Property: `right & (right - 1)` clears the **lowest set bit** of `right`.
// Repeatedly clearing lowest bits while right > left removes trailing variation
// until right collapses to **left’s prefix**, yielding the same answer:
//
//   while left < right:
//       right &= right - 1
//   return right
//
// Same asymptotics; sometimes cited as “Brian Kernighan style.” Choose **A** in
// interviews when you want the clearest **prefix** story; choose **B** as a compact
// trick if the interviewer likes bit hacks.
//
// =============================================================================
// DATA STRUCTURES
// =============================================================================
//
// **None** beyond a few scalar integers — **O(1)** space. No arrays, trees, or
// lookup tables; the problem is purely bitwise on **left**, **right**, **shift**.
//
// =============================================================================
// EDGE CASES
// =============================================================================
//
// - **left == right:** AND of one number is that number; loop runs 0 times.
// - **left = 0:** valid; shifting handles zeros naturally.
// - **Large intervals:** still logarithmic iterations — no overflow if using
//   language arbitrary-precision ints (Python); in Go, use int with 32-bit constraints.
//
// =============================================================================
// TESTING
// =============================================================================
//
// - Brute force on tiny ranges vs optimized routine for random small [left, right].
// - Known: [5,7] → 4; [0,1] → 0; [8,15] → 8.
//
// =============================================================================
// POSSIBLE IMPROVEMENTS / VARIANTS
// =============================================================================
//
// - **Leading-zero bit-length:** compute common prefix via **msb(left ⊕ right)**
//   and mask — **O(1)** arithmetic if hardware supports fast **log2** / CLZ
//   (count leading zeros); portable code often stays with the shift loop.
// - **Faster on fixed width:** once bit-width W is fixed (e.g. 32-bit), loop runs
//   at most W times — still **O(log U)** in value magnitude.
//
// =============================================================================

// RangeBitwiseAnd201 returns the bitwise AND of all integers in [left, right].
func RangeBitwiseAnd201(left int, right int) int {
	shift := 0
	for left != right {
		left >>= 1
		right >>= 1
		shift++
	}
	return left << shift
}

