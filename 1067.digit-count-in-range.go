//
// @lc app=leetcode id=1067 lang=python3
//
// [1067] Digit Count in Range
//
//
// --- Interview notes (range reduction, digit DP state machine, leading zeros, complexity, edges, tests) ---
//
// Problem
// Given digit d ∈ [0,9] and integers low ≤ high, count how many times digit d appears in the decimal writing of
// all integers x with low ≤ x ≤ high (count multiplicity per integer, e.g. 11 contributes two 1’s).
//
// Range reduction
// Let F(N) = total occurrences of digit d in all integers x with 0 ≤ x ≤ N (decimal, no leading zeros except the
// number 0 itself handled via leading-zero mechanics).
// Answer = F(high) − F(low − 1).
//
// Why digit DP instead of iterating [low, high]
// high − low can be ~2·10^8 — scanning every integer is too slow.
//
// Digit DP model (count occurrences, not count numbers)
// Decompose N into digits a[1..L] with a[1] = least significant digit (editorial indexing). DFS processes from
// position L down to 1 (most significant → least).
// State:
//   pos   — next digit position to fix.
//   cnt   — how many copies of digit d have been placed so far on this path.
//   lead  — still placing leading zeros before the number truly starts (important when d = 0).
//   limit — tight to prefix of N (cannot exceed N).
// Transition: try digit i ∈ [0, up] where up = a[pos] if limit else 9.
//   • If i == 0 and lead: still “no real digit yet” → recurse with lead True (still flexible), cnt unchanged.
//   • Else the number has started; count += 1 if i == d; lead becomes False.
// Base pos ≤ 0: return cnt.
//
// Memoization
// Python functools.cache on dfs; states bounded by pos ≤ 10, cnt ≤ 10, booleans — tiny graph.
// (Java editorial memoizes only when ¬lead ∧ ¬limit for speed; cache-all is fine here.)
//
// Special role of digit 0
// Leading zeros before the first non-zero digit must not be counted as occurrences of ‘0’ (otherwise every
// shorter-length padding would inflate zeros). The lead flag suppresses those.
//
// Time complexity
// O(log10 N) positions × O(10) digit choices × memo hits → effectively O(log N) per F(N), two calls total.
//
// Space complexity
// O(log N) recursion depth + memo table negligible.
//
// Alternative (mention only)
// Closed-form digit enumeration (“rotate factor” method from CS interviews) counts occurrences in O(log N)
// without recursion — useful when memo limits matter; digit DP is easier to derive under pressure.
//
// Edge cases
// low = 1 ⇒ low − 1 = 0 ⇒ F(0) = 0 with our extraction loop (no digits → dfs returns 0 immediately).
// d = 0 needs correct leading-zero handling (validated via brute tests).
//
// Tests (statement)
// d = 1, low = 1, high = 13 → 6.
// d = 3, low = 100, high = 250 → 35.
//
// Improvements
// - Iterative DP table instead of recursion if stack depth ever matters (not here).
//
// --- end notes ---
//
// @lc code=start

package leetcode

func DigitsCount1067(d int, low int, high int) int {
	var upto func(n int) int
	upto = func(n int) int {
		if n < 0 {
			return 0
		}

		// a[1..l], a[1] is least significant digit.
		a := make([]int, 11)
		l := 0
		for t := n; t > 0; t /= 10 {
			l++
			a[l] = t % 10
		}

		// memo[pos][cnt][lead][limit]
		memo := make([][][][]int, l+1)
		seen := make([][][][]bool, l+1)
		for pos := 0; pos <= l; pos++ {
			memo[pos] = make([][][]int, l+1)
			seen[pos] = make([][][]bool, l+1)
			for cnt := 0; cnt <= l; cnt++ {
				memo[pos][cnt] = make([][]int, 2)
				seen[pos][cnt] = make([][]bool, 2)
				for lead := 0; lead < 2; lead++ {
					memo[pos][cnt][lead] = make([]int, 2)
					seen[pos][cnt][lead] = make([]bool, 2)
				}
			}
		}

		var dfs func(pos int, cnt int, lead bool, limit bool) int
		dfs = func(pos int, cnt int, lead bool, limit bool) int {
			if pos <= 0 {
				return cnt
			}
			li, lo := 0, 0
			if lead {
				li = 1
			}
			if limit {
				lo = 1
			}
			if seen[pos][cnt][li][lo] {
				return memo[pos][cnt][li][lo]
			}
			seen[pos][cnt][li][lo] = true

			up := 9
			if limit {
				up = a[pos]
			}
			total := 0
			for i := 0; i <= up; i++ {
				if i == 0 && lead {
					total += dfs(pos-1, cnt, true, limit && i == up)
				} else {
					add := 0
					if i == d {
						add = 1
					}
					total += dfs(pos-1, cnt+add, false, limit && i == up)
				}
			}
			memo[pos][cnt][li][lo] = total
			return total
		}

		return dfs(l, 0, true, true)
	}

	return upto(high) - upto(low-1)
}

// @lc code=end

