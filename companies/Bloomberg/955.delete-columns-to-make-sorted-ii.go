package leetcode

//
// @lc app=leetcode id=955 lang=golang
//
// [955] Delete Columns To Make Sorted Ii
//

// --- Interview notes (lexicographic order, greedy columns, “locked” pairs, complexity) ---
//
// Problem
// **`strs`** is an array of **`n`** equal-length strings (rows). You may **delete** any subset of **column indices** in **all** rows
// (same columns removed everywhere). After deletions, reading each row’s remaining characters **left to right** must yield
// **`strs[0] ≤ strs[1] ≤ … ≤ strs[n-1]`** in **lexicographic** order. Return the **minimum** number of columns to delete.
//
// Lexicographic **≤** for two rows
// Compare the two strings **column by column** (on **kept** columns only, in order). At the **first** position where they differ, we
// need the **upper** row’s character **≤** the **lower** row’s. If they **never** differ on kept columns, the two rows are **equal** as
// substrings — that is allowed (**`≤`** with equality).
//
// Key invariant — “locked” adjacent pairs
// For each adjacent pair **`(i, i+1)`**, if among **already kept** columns we have already seen **`strs[i] < strs[i+1]`** at the **first**
// differing kept column, that pair is **finished**: no future column can break **`strs[i] ≤ strs[i+1]`** (lex order is decided). Call
// such a pair **locked** (boolean **`done[i]`** in code).
// If a pair is **not** locked yet, the two rows are **still equal** on all kept columns so far; the **next** kept column must satisfy
// **`strs[i][c] ≤ strs[i+1][c]`**; a strict **`>`** at any future kept column would make the pair unsortable, so that column **cannot** be
// kept.
//
// Greedy (left to right) is optimal
// Process columns **in order** (index **`j = 0 … m-1`**). For the current column **`j`**, if **every** **unlocked** adjacent pair
// satisfies **`strs[i][j] ≤ strs[i+1][j]`**, we **keep** the column: then **lock** every pair with **`strs[i][j] < strs[i+1][j]`**
// (strictly smaller — the order between those two rows is now fixed as **<** for the full rows). If **any** unlocked pair has
// **`strs[i][j] > strs[i+1][j]`**, this column would **violate** **`≤`** for that pair, so we **delete** it (increment answer) and
// **do not** update locks.
// • Keeping a column **never** makes a previously valid final order invalid (we only add constraints that are satisfiable or skip).
// • Deleting a column is forced when it would break an unlocked pair; skipping it is always safe and never increases the need for
//   future deletions in a way that a different global choice would improve — the classic exchange / greedy argument for this problem
//   class.
//
// Data structures
// • **`done[i]`** for **`i in range(n-1)`** — **`O(n)`** booleans, no other heavy structure.
// • Input is the string matrix; we only **read** characters **by index**.
//
// Time complexity **`O(n · m)`** — for each of **`m`** columns, scan **`n-1`** adjacent pairs.
//
// Space complexity **`O(n)`** for **`done`**, output count **ignores** input size in auxiliary space.
//
// Edge cases
// • **`n == 1`** — no adjacent pair; **any** column set works → **`0`** deletions.
// • **All rows already non-decreasing** in every column for unlocked pairs — **keep** everything → **`0`**.
// • **Duplicate rows** — equality is allowed; pairs may stay **unlocked** until the end (still **≤**).
//
// Tests (LeetCode)
// • **`["ca","aa","ab"]`** → **`1`** (column **0** breaks row **0** vs **1**).
// • **`["xc","yb","za"]`** → **`0`** (column **0** strictly sorts each consecutive pair).
// • **`["zyx","wvu","tsr"]`** → **`3`** (every column has a **`>`** somewhere among unlocked pairs).
//
// Improvements
// • **Early exit** is optional if **`done`** all **`True`** — every pair locked (optional micro-optimization).
// • **955-I** (sorted **I**) deletes columns so **each column alone** is sorted — weaker constraint; **II** couples rows lexicographically.
//
// --- end notes ---

// @lc code=start

func MinDeletionSize955(strs []string) int {
	n := len(strs)
	if n <= 1 {
		return 0
	}
	m := len(strs[0])
	done := make([]bool, n-1)
	removed := 0
	for j := 0; j < m; j++ {
		ok := true
		for i := 0; i < n-1; i++ {
			if !done[i] && strs[i][j] > strs[i+1][j] {
				ok = false
				break
			}
		}
		if !ok {
			removed++
			continue
		}
		for i := 0; i < n-1; i++ {
			if !done[i] && strs[i][j] < strs[i+1][j] {
				done[i] = true
			}
		}
	}
	return removed
}

// @lc code=end
