package leetcode

//
// @lc app=leetcode id=931 lang=golang
//
// [931] Minimum Falling Path Sum
//

// --- Interview notes (grid DP, optimal substructure, rolling array, complexity) ---
//
// Problem
// Given an **`n × n`** integer **matrix**, a **falling path** starts in **any** column of the **top** row and moves **down** one row at
// a time. From **`(i, j)`** the next row may be **`(i+1, j-1)`**, **`(i+1, j)`**, or **`(i+1, j+1)`** (stay in bounds). The **path sum** is
// the sum of visited cells. Return the **minimum** path sum over all valid falling paths.
//
// Optimal substructure
// Let **`dp[i][j]`** = minimum sum to reach **`(i, j)`** from some start in row **0**. Then
// **`dp[i][j] = matrix[i][j] + min(dp[i-1][j-1], dp[i-1][j], dp[i-1][j+1])`**, treating out-of-bounds neighbors as **inf** (or only take
// existing columns). The answer is **`min_j dp[n-1][j]`**.
//
// Why dynamic programming
// The graph of allowed moves is a **layered DAG** (row index always increases), so there are **no cycles**; shortest / min-sum paths
// satisfy the **Principle of Optimality** — any prefix of a minimum path to **`(i,j)`** is itself minimum to its endpoint. **DP** is
// natural; **BFS** with weights or **Dijkstra** is overkill for this small local transition.
//
// Space optimization
// Row **`i`** only depends on row **`i-1`**. Two **length-`n`** arrays (**prev**, **cur**) or **one** array updated left-to-right or
// right-to-left with care — we use **two rows** for clarity (**`O(n)`** space).
//
// Data structures
// **Two `list[int]`** rows — no `heap`, no 2D table required for production space.
//
// Time complexity **`O(n²)`** — each of **`n²`** cells, **`O(1)`** work.
//
// Space complexity **`O(n)`** auxiliary (**`O(n²)`** if you store full **`dp`** table for reconstruction or debugging).
//
// Edge cases
// • **`n == 1`** — answer is the single cell.
// • **First row** — **`dp[0][j] = matrix[0][j]`** (or initialize **`prev`** from **`matrix[0]`**).
//
// Tests (LeetCode)
// • **`[[2,1,3],[6,5,4],[7,8,9]]`** → **`13`** (e.g. **1 → 4 → 8**).
//
// Improvements
// • **In-place** on **`matrix`** bottom-up overwrites data — **`O(1)`** extra if mutation allowed.
// • **Path reconstruction** — keep **`parent` column** or full table.
//
// --- end notes ---

// @lc code=start

func MinFallingPathSum931(matrix [][]int) int {
	n := len(matrix)
	if n == 0 {
		return 0
	}
	m := len(matrix[0])
	prev := make([]int, m)
	copy(prev, matrix[0])
	for i := 1; i < n; i++ {
		cur := make([]int, m)
		for j := 0; j < m; j++ {
			v := prev[j]
			if j > 0 && prev[j-1] < v {
				v = prev[j-1]
			}
			if j+1 < m && prev[j+1] < v {
				v = prev[j+1]
			}
			cur[j] = matrix[i][j] + v
		}
		prev = cur
	}
	out := prev[0]
	for j := 1; j < m; j++ {
		if prev[j] < out {
			out = prev[j]
		}
	}
	return out
}

// @lc code=end
