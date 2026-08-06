package leetcode

//
// LeetCode 1163 — Last Substring In Lexicographical Order
//
// --- Interview notes (reduce to max suffix, two-pointer duel, complexity, edges, alternatives) ---
//
// Problem
// Among all contiguous substrings of `s`, return the lexicographically largest one (string comparison in dictionary order).
//
// Key reduction — optimal substring always ends at the last character
// Suppose an optimal substring is s[l : r+1] with r < n - 1. Compare it with s[l : r+2] (one character longer on the
// right). They agree on the first (r - l + 1) characters; at the next position the longer substring has a concrete
// character while the shorter has “nothing” — so the longer is lexicographically larger. Hence any non-maximal-right-end
// substring can be strictly improved by extending to index n - 1.
// Therefore the answer is always s[i:] for some starting index i ∈ [0, n - 1] — i.e. **some suffix of s**.
//
// Reformulation
// Find the suffix of `s` that is lexicographically maximum among all n suffixes.
//
// Naive approach
// Compare every pair of suffixes — O(n²) character comparisons worst-case; too slow for |s| up to 4·10⁵ (LeetCode).
//
// Chosen approach — O(n) two-pointer “suffix duel” (Booth–Duval style idea)
// Maintain index `i` = current best candidate for where the maximum suffix starts, and `j` = challenger start (`j > i`).
// Compare characters with offset `k`: s[i+k] vs s[j+k].
// • Equal → increase k (common prefix of the two suffixes grows).
// • s[i+k] < s[j+k] → suffix starting at `i` loses to suffix starting at `j` at the first differing position. Any start
//   index in [i, i+k] also loses to `j` (those suffixes share the bad prefix relative to j). Jump `i` past that block:
//   `i ← max(i + k + 1, j)` so we never revisit discarded positions; reset `k`, and set `j ← i + 1` as the next challenger.
// • s[i+k] > s[j+k] → challenger loses; advance `j` past the mismatched block: `j ← j + k + 1`, reset `k`.
// Loop while `j + k < n` (room for challenger suffix). Return `s[i:]`.
//
// Why `i ← max(i + k + 1, j)`?
// After proving suffix at `i` is worse than suffix at `j`, starts strictly between `i` and `j` can also be eliminated or
// must stay consistent with ordering — the `max` avoids moving `i` backward when `j` had already passed `i+k+1`.
//
// Time complexity
// Each failed comparison advances either `i` or `j` by at least one; pointer moves sum to O(n); `k` resets but total work
// is linear — **O(n)** character comparisons amortized.
//
// Space complexity
// **O(1)** extra (only indices); output substring shares underlying storage view in theory (Python slice copies — problem
// treats return as conceptual).
//
// Edge cases
// • |s| = 1 → answer is `s`.
// • All characters equal → every suffix begins with the same run; algorithm returns **whole string** `s` (maximum suffix
//   is s[0:]).
//
// Tests (sanity / statement-style)
// • "leetcode" → "tcode"
// • "abab" → "bab"
// • "a" → "a"
// • "aaa" → "aaa"
//
// Alternative algorithms (trade-offs)
// • **Suffix array + LCP** in O(n log n) or O(n) — overkill here but generalizes to many suffix queries.
// • **Rolling hash + binary search** per pair — still slower than linear two-pointer for single max suffix.
// • **Naive** compare all suffix pairs — O(n²), simple but fails constraints.
//
// Improvements
// • Implementation uses only integer indices — cache-friendly, no auxiliary arrays.
// • For interviews, prove “answer is a suffix ending at n−1” first, then present two-pointer duel as linear-time max suffix.
//
// --- end notes ---
//

// LastSubstring1163 returns the lexicographically largest substring of s.
func LastSubstring1163(s string) string {
	i, j, k := 0, 1, 0
	n := len(s)
	for j+k < n {
		a := s[i+k]
		b := s[j+k]
		if a == b {
			k++
			continue
		}
		if a < b {
			ni := i + k + 1
			if ni < j {
				ni = j
			}
			i = ni
			k = 0
			j = i + 1
		} else {
			j = j + k + 1
			k = 0
		}
	}
	return s[i:]
}

