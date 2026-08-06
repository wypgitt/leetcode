package leetcode

import "sort"

//
// LeetCode 260 — Single Number III
//
// =============================================================================
// PROBLEM (precise)
// =============================================================================
//
// Every integer in nums appears **exactly twice**, except **two distinct integers**
// that appear **exactly once**. Return those two singletons (order arbitrary unless
// the judge fixes it).
//
// =============================================================================
// WHY XOR (algorithm choice)
// =============================================================================
//
// **Pairs cancel:** For any x, **x XOR x = 0**. So if we XOR **all** elements,
// every duplicated value vanishes and we’re left with **a XOR b**, where **a** and
// **b** are the two unique numbers we want.
//
// We **cannot** recover a and b from **a XOR b** alone — information is missing — but
// we can **split** the array using one distinguishing bit between **a** and **b**.
//
// Let **s = a XOR b**. Since **a ≠ b**, **s ≠ 0**, so **s** has at least one bit set.
// Pick **any** such bit (common trick: the **lowest** set bit **lowbit(s) = s & -s**
// in two’s-complement arithmetic). Then **a** and **b** differ on that bit — one has
// it 0, the other 1.
//
// **Partition** nums into two groups: numbers whose bit is 0 vs 1 at that position.
// - Duplicated numbers **always land in the same group together**, so they still
//   cancel within each group when XOR-reduced.
// - The two singletons land in **different** groups, so each group’s XOR reduces to
//   exactly **one** of **{a, b}**.
//
// Two linear passes: **O(n)** time, **O(1)** extra space (only integers / two XOR
// accumulators). No hash map needed — though a frequency map also works in **O(n)**
// time but **O(n)** space; XOR is the canonical “interview elegant” answer.
//
// =============================================================================
// DATA STRUCTURES
// =============================================================================
//
// - **Scalars only:** running XOR **s**, bitmask **diff**, two XOR buckets **x** and
//   **y** (or reuse pattern with two accumulators). **No** auxiliary arrays sized by
//   **n** — **O(1)** extra space beyond the input list reference.
//
// =============================================================================
// TIME & SPACE COMPLEXITY (analysis)
// =============================================================================
//
// **Time:** Two passes over **nums** → **O(n)**.
// **Space:** Constant extra integers → **O(1)** (output list of length 2 does not
// dominate asymptotics).
//
// Compare: sorting **O(n log n)**; HashMap counts **O(n)** time and **O(n)** space.
//
// =============================================================================
// EDGE CASES
// =============================================================================
//
// - **Exactly two distinct singletons** guaranteed when input valid — smallest size is
//   often **4** elements (two pairs + pattern varies); problem guarantees existence.
// - **Negative numbers:** XOR / bit tests behave consistently on two’s-complement
//   representations in Go; **lowbit** trick still valid.
// - **Return order:** problem typically accepts either order; sorting the pair is a
//   harmless normalization for debugging / deterministic tests.
//
// =============================================================================
// TESTING
// =============================================================================
//
// - Known example(s) from statement.
// - Random stress: build multiset with pairs + two distinct values; XOR solution vs
//   Counter-reference on many seeds.
// - Edge: range of ints including negatives.
//
// =============================================================================
// POSSIBLE VARIANTS / IMPROVEMENTS
// =============================================================================
//
// - Choose **any** set bit of **s** (not only lowbit), e.g. iterate bit index — same
//   asymptotics, slightly more code.
// - If overflow were an issue (not in Go int for LC 32-bit), still XOR in fixed-width **unsigned**
//   interpretation for the bit test.
//
// =============================================================================

// SingleNumberIII260 returns the two integers that appear exactly once; all others appear twice.
func SingleNumberIII260(nums []int) []int {
	xorAB := 0
	for _, x := range nums {
		xorAB ^= x
	}

	// Lowest set bit of (a ^ b): a and b differ here; pairs share fate per group.
	diffBit := xorAB & (-xorAB)

	a, b := 0, 0
	for _, x := range nums {
		if x&diffBit != 0 {
			a ^= x
		} else {
			b ^= x
		}
	}

	out := []int{a, b}
	sort.Ints(out)
	return out
}

