package leetcode

//
// @lc app=leetcode id=916 lang=golang
//
// [916] Word Subsets
//

// =============================================================================
// INTERVIEW: ELEVATOR PITCH (~30 seconds)
// =============================================================================
//
// "For each string A in words1, we need A to **cover** every string in words2 as a
// **multiset of letters**: we can only use letters from A, so B is 'covered' if for
// every letter, count_B(letter) ≤ count_A(letter). Checking A against every B
// separately is slow; instead we **merge** all B's into one requirement vector:
// for each letter, take the **maximum** count needed across all B. Then test each A
// once against that 26-slot fingerprint — O(total characters) with O(1) extra."
//
// =============================================================================
// PROBLEM (PRECISE)
// =============================================================================
//
// • words1 = candidate strings (answer must be a sublist of these, preserve order
//   of first occurrence if problem asks — here return any order of qualifying words;
//   LeetCode expects order **same as words1** scan).
// • words2 = constraint strings. A candidate A is **universal** iff for **every**
//   B in words2, B is a **subset** of A in the letter-multiset sense (you can spell
//   B using letters from A with multiplicity).
//
// Equivalently: freq_A(L) ≥ freq_B(L) for every letter L and every B in words2.
//
// =============================================================================
// KEY IDEA — MERGE CONSTRAINTS (WHY MAX, NOT SUM)
// =============================================================================
//
// Naively: for each A, loop all B and verify inclusion — worst-case multiplies
// |words1| × |words2| × alphabet work.
//
// Observe: letters are **independent** across positions in B. For a fixed letter
// `c`, the **strongest** lower bound on freq_A(c) among all B is:
//
//       needed(c) = max_{B in words2} freq_B(c)
//
// Because if some word needs 3 copies of 'e' and another needs 1, having **3** e's
// in A satisfies **both**; summing would **over-count** (you reuse the same letter
// occurrences when satisfying multiple B's on the same A).
//
// So build one array **req[26]** where req[i] = max frequency of letter i across all
// strings in words2 (after counting each B once).
//
// Then A is universal iff freq_A(i) ≥ req[i] for all i ∈ [0,25].
//
// =============================================================================
// ALGORITHM
// =============================================================================
//
// 1. req ← array of 26 zeros.
// 2. For each string b in words2:
//        cnt ← letter counts of b (length-26 vector).
//        For each i: req[i] ← max(req[i], cnt[i]).
// 3. ans ← empty list.
// 4. For each string a in words1:
//        cnt ← letter counts of a.
//        If cnt[i] ≥ req[i] for all i, append a to ans.
// 5. Return ans.
//
// =============================================================================
// DATA STRUCTURES — WHY LENGTH-26 ARRAYS (NOT HASH MAPS)
// =============================================================================
//
// Alphabet is **fixed lowercase English** (a–z). A length-26 integer array gives:
//   • O(1) random access per letter index.
//   • No hashing overhead; cache-friendly tiny vector.
//   • Easy comparison with **element-wise ≥**.
//
// **Counter / dict** is fine in Python interviews but arrays make the bit-vector
// story crisp and match C++/Java ports literally.
//
// =============================================================================
// TIME & SPACE COMPLEXITY
// =============================================================================
//
// Let:
//   N1 = sum of |w| over w in words1
//   N2 = sum of |w| over w in words2
//
// Building req: O(N2). Testing words1: O(N1). Comparisons are 26 checks per word
// in words1 → O(26 × |words1|) ⊆ O(N1 + |words1|) — linear in **total characters**
// plus linear in number of candidates.
//
// Overall **time: O(N1 + N2)** (alphabet size 26 is constant factor).
//
// **Space:** O(1) besides output — req is 26 ints; each count array is 26 ints on
// the stack / ephemeral (not stored simultaneously for all words). Output list
// holds up to |words1| strings (required).
//
// =============================================================================
// EDGE CASES
// =============================================================================
//
// • words2 empty — problem constraints usually guarantee non-empty; if empty,
//   req stays zero → **every** word in words1 qualifies (every string covers vacuous
//   constraints).
// • Single-letter repeats: B = "oo" forces req['o'] ≥ 2.
// • words1 with duplicates — if same string appears twice, include twice if both
//   pass (problem: words1 is list — typically keep both).
// • A shorter than any B — fails when some req[i] > 0 exceeds count in A.
//
// =============================================================================
// TESTING (MENTAL / UNIT)
// =============================================================================
//
// • words1 = ["amazon","apple","facebook","google","leetcode"],
//   words2 = ["e","o"] → req: e≥1, o≥1 → ["facebook","google","leetcode"].
// • words2 = ["lo","eo"] → 'l' max 1, 'o' max 1, 'e' max 1 → same check.
// • words2 = ["loo","eo"] → need o from "loo" → o≥2.
//
// Property: merged req is **monotone** — adding more words to words2 can only
// increase req coordinate-wise, never shrink the answer set.
//
// =============================================================================
// IMPROVEMENTS / VARIANTS
// =============================================================================
//
// • **Early rejection:** while scanning counts for a, break on first i with
//   cnt[i] < req[i] — same asymptotics, fewer branches in tight loops.
// • **Bit tricks:** not worthwhile for 26 letters vs scalar compare.
//
// =============================================================================

// @lc code=start

// WordSubsets916 returns all words in words1 that contain every words2 string as a letter-multiset subset.
//
// Merges words2 into a single requirement vector req[c] = max frequency of c
// across all strings in words2; then filters words1 by freq(w) >= req pointwise.
func WordSubsets916(words1, words2 []string) []string {
	req := [26]int{}
	for _, b := range words2 {
		cntB := letterCounts916(b)
		for i := 0; i < 26; i++ {
			if cntB[i] > req[i] {
				req[i] = cntB[i]
			}
		}
	}

	var ans []string
	for _, a := range words1 {
		cntA := letterCounts916(a)
		if covers916(cntA, req) {
			ans = append(ans, a)
		}
	}
	return ans
}

func letterCounts916(s string) [26]int {
	var c [26]int
	base := int('a')
	for i := 0; i < len(s); i++ {
		c[int(s[i])-base]++
	}
	return c
}

func covers916(cntA [26]int, req [26]int) bool {
	for i := 0; i < 26; i++ {
		if cntA[i] < req[i] {
			return false
		}
	}
	return true
}

// @lc code=end
