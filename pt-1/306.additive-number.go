//
// @lc app=leetcode id=306 lang=python3
//
// [306] Additive Number
//

// @lc code=start

package leetcode

// @lc code=end
//
// @lc app=leetcode id=306 lang=python3
//
// [306] Additive Number
//
// =============================================================================
// INTERVIEW: HOW TO EXPLAIN (elevator → whiteboard)
// =============================================================================
//
// 30 seconds:
//   "Split the digit string into a Fibonacci-like sequence: after the first two
//   numbers, each segment must equal the sum of the previous two. I try every
//   valid split for the first two numbers; once chosen, the rest of the string
//   is forced — greedily match each next sum left-to-right. Leading zeros are
//   illegal except for the single digit '0'."
//
// 2–4 minutes:
//   - Brute structure: backtracking could branch heavily; key observation is that
//     after fixing n1 and n2, every later term is uniquely determined (must equal
//     n_{k-2}+n_{k-1}), so we only branch on where the first two numbers end.
//   - Loop split positions: first number num[0:i], second num[i:j]; both must be
//     valid numeric segments (no multi-digit token starting with '0').
//   - From position j, repeatedly expect next = add(prev2, prev1) as a decimal
//     string prefix of the remainder; advance pointer by len(next). Success iff we
//     consume the whole string and extended beyond j (≥ 3 numbers total).
//   - Arithmetic: use Python int (arbitrary precision). In languages with 64-bit
//     limits, use BigInteger or implement schoolbook string addition.
//
// =============================================================================
// ALGORITHM
// =============================================================================
//
// For each i in [1, n-2] (length of first number) and j in [i+1, n-1] (end of
// second number exclusive):
//   a = num[0:i], b = num[i:j]
//   If invalid segment(s), continue.
//   k = j; x, y = a, b
//   While k < n:
//       z = decimal string for int(x) + int(y)   # next Fibonacci term
//       If num does not have prefix z at k, break.
//       k += len(z); x, y = y, z
//   If k == n and k > j, return True   # used at least one term after b
// Return False
//
// =============================================================================
// DATA STRUCTURES
// =============================================================================
//
// - Only indices into `num` and a few string slices; no auxiliary containers.
// - Optional: cache int(x) if profiling; not required for LC sizes.
//
// =============================================================================
// COMPLEXITY
// =============================================================================
//
// Let L = len(num). Try O(L^2) pairs (i, j). Verification is O(L) per pair in
// the worst case (linear scan with possibly growing digit lengths).
// Overall time O(L^3); space O(L) for slices / recursion stack if any (here O(1)
// extra besides input).
//
// =============================================================================
// EDGE CASES
// =============================================================================
//
// - Length < 3: cannot form three numbers → False.
// - Leading zeros: "01", "001" as a segment invalid unless the segment is exactly
//   "0".
// - "000": valid as 0 + 0 = 0 (three numbers).
// - "111": no valid additive split → False.
// - Large integers: Python int OK; mention BigInteger in Java-style interviews.
//
// =============================================================================
// TESTING
// =============================================================================
//
// Known cases:
//   - "112358" → True (classic Fibonacci digits).
//   - "199100199" → True (1, 99, 100, 199).
//   - "1023" → False.
// Property: if True, simulate parsing and verify each sum from prior two.
//
// =============================================================================
//
// @lc code=start

func IsAdditiveNumber306(num string) bool {
	//
	// Return True iff `num` can be split into ≥ 3 parts forming an additive
	// sequence (Fibonacci-like), with no illegal leading zeros on segments.
	//

	validSegment := func(s string) bool {
		return len(s) > 0 && (len(s) == 1 || s[0] != '0')
	}

	addStrings := func(a, b string) string {
		i, j := len(a)-1, len(b)-1
		carry := 0
		out := make([]byte, 0, maxInt306(len(a), len(b))+1)
		for i >= 0 || j >= 0 || carry != 0 {
			sum := carry
			if i >= 0 {
				sum += int(a[i] - '0')
				i--
			}
			if j >= 0 {
				sum += int(b[j] - '0')
				j--
			}
			out = append(out, byte(sum%10)+'0')
			carry = sum / 10
		}
		for l, r := 0, len(out)-1; l < r; l, r = l+1, r-1 {
			out[l], out[r] = out[r], out[l]
		}
		return string(out)
	}

	n := len(num)
	if n < 3 {
		return false
	}

	for i := 1; i < n-1; i++ {
		for j := i + 1; j < n; j++ {
			first := num[:i]
			second := num[i:j]
			if !validSegment(first) || !validSegment(second) {
				continue
			}

			k := j
			x, y := first, second
			for k < n {
				nxt := addStrings(x, y)
				if k+len(nxt) > n || num[k:k+len(nxt)] != nxt {
					break
				}
				k += len(nxt)
				x, y = y, nxt
			}

			if k == n && k > j {
				return true
			}
		}
	}
	return false
}

func maxInt306(a, b int) int {
	if a > b {
		return a
	}
	return b
}

// @lc code=end

