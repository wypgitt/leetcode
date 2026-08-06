package leetcode

//
// @lc app=leetcode id=984 lang=golang
//
// [984] String Without Aaa Or Bbb
//

// --- Interview notes (greedy scheduling, run-length cap 2, ties, feasibility, complexity) ---
//
// Problem
// Build a string with exactly **`a`** copies of **`'a'`** and **`b`** copies of **`'b'`** such that **no three consecutive**
// characters are identical (**no `"aaa"` or `"bbb"`**).
//
// Greedy strategy
// Always append from the side that still has **more** letters remaining (**`a > b`** → prefer **`'a'`**, else prefer **`'b'`**),
// **except** when the last two characters are already the same — then we **must** append the **other** letter next (if any
// left) to break a length-3 run.
//
// Implementation split
// • **`a == 0`** or **`b == 0`** — only one letter remains; any valid string is a run of that letter of length **`≤ 2`** (LeetCode
//   guarantees feasibility so counts fit).
// • **`a > b`** branch: if suffix is **`"aa"`**, append **`'b'`**; else append **`'a'`**.
// • **`a ≤ b`** branch (covers **`a < b`** and **`a == b`**): if suffix is **`"bb"`**, append **`'a'`**; else append **`'b'`**.
//
// Why `a == b` goes to the second branch
// Symmetric case; choosing the **`b`**-first tie-break matches common references and keeps **`aa`** / **`bb`** checks aligned.
//
// Feasibility (background)
// A solution exists iff **`max(a,b) ≤ 2·min(a,b) + 2`** when **`a,b > 0`** (and single-letter cases need length **`≤ 2`**). The
// judge inputs satisfy this; otherwise no valid string exists.
//
// Data structures
// **`list` of chars** (or build **`list`** and **`join`**) — **O(a+b)`** output only.
//
// Time complexity **O(a + b)`** — one append decision per character placed.
//
// Space complexity **O(a + b)`** for the result string (**O(1)** beyond output if streaming not required).
//
// Edge cases
// • **`a = b = 0`** — empty string.
// • **`a + b = 1`** — single character.
//
// Tests
// • **`a = 1`, `b = 2`** → **`"bab"`** (many permutations valid).
//
// Improvements
// • **Pattern blocks** (`"aab"`, `"bba"`) batch emission when counts highly skewed — can shorten constant factors; greedy above
//   is simpler to defend in interviews.
//
// --- end notes ---

// @lc code=start

// StrWithout3a3b984 builds a string with exactly a 'a's and b 'b's with no "aaa" or "bbb".
func StrWithout3a3b984(a int, b int) string {
	if a == 0 && b == 0 {
		return ""
	}
	if a == 0 {
		out := make([]byte, b)
		for i := range out {
			out[i] = 'b'
		}
		return string(out)
	}
	if b == 0 {
		out := make([]byte, a)
		for i := range out {
			out[i] = 'a'
		}
		return string(out)
	}

	out := make([]byte, 0, a+b)
	for a > 0 || b > 0 {
		if a > b {
			if len(out) >= 2 && out[len(out)-1] == 'a' && out[len(out)-2] == 'a' {
				out = append(out, 'b')
				b--
			} else {
				out = append(out, 'a')
				a--
			}
		} else {
			if len(out) >= 2 && out[len(out)-1] == 'b' && out[len(out)-2] == 'b' {
				out = append(out, 'a')
				a--
			} else {
				out = append(out, 'b')
				b--
			}
		}
	}
	return string(out)
}

// @lc code=end

