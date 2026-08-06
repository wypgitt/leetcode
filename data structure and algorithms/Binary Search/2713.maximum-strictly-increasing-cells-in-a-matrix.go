package leetcode

//
// @lc app=leetcode id=2713 lang=golang
//
// [2713] Maximum Strictly Increasing Cells in a Matrix
//
// --- Interview notes (model, DP state, same-value batching, complexity, edges, tests) ---
//
// Problem (summary)
// From any starting cell, repeatedly move to another cell in the SAME ROW or SAME COLUMN whose value is
// STRICTLY GREATER than the current value. Maximize the number of visited cells (path length), choosing the
// best start.
//
// Why greedy “longest path in DAG” by raw DFS fails
// The implicit graph can have many overlapping paths; naive DFS/backtracking is exponential. Values give a
// topological order: every step strictly increases the value, so no cycles.
//
// Key observation — only value order matters
// Any legal walk visits strictly increasing values. So processing cells in non-decreasing order of mat[i][j]
// respects every possible transition direction (always from smaller value to larger value).
//
// DP state
// After processing all cells with values < v, define:
//   rowMax[i] = best (maximum) path length achievable ending in row i using only cells with value < v.
//   colMax[j] = same for column j.
// To extend into a cell (i, j) with value v, the previous cell must lie in row i or column j with smaller
// value, so the best length ending at (i, j) using smaller values is:
//   bestPrev = max(rowMax[i], colMax[j])
//   dp(i,j) = 1 + bestPrev
//
// Why two passes within the same value group
// All cells sharing the same value cannot be used on consecutive steps (strict inequality). If we updated
// rowMax/colMax immediately after each cell, two equal-valued cells in the same row could incorrectly treat
// each other as predecessors. Correct fix: for each value v, FIRST compute every cell’s dp using frozen
// rowMax/colMax from strictly smaller values; ONLY THEN merge these dp values back into rowMax/colMax.
//
// Algorithm
// 1. Bucket positions by mat[i][j] (hash map / defaultdict).
// 2. For v in sorted(distinct values ascending):
//      For each (i, j) in bucket[v]: mx[k] = 1 + max(rowMax[i], colMax[j]); track global answer.
//      Then for each k: rowMax[i] = max(rowMax[i], mx[k]), colMax[j] = max(colMax[j], mx[k]).
// 3. Return answer.
//
// Data structures
// - Dictionary value -> list of (i, j): O(mn) positions total.
// - rowMax length m, colMax length n: O(m + n).
// Sorting keys: O(K log K) for K distinct values, K <= mn.
//
// Time complexity
// O(mn) to build buckets + O(K log K) sort + O(mn) scans → O(mn log(mn)) worst-case when K ~ mn.
//
// Space complexity
// O(mn) for buckets (+ output-sized); O(m + n) for DP arrays.
//
// Edge cases
// - Constant matrix: every cell same value → only length 1 anywhere → answer 1 (Example 2).
// - Single cell: answer 1.
// - mn <= 1e5 ensures sorting/buckets stay feasible.
//
// Tests (statement)
// mat = [[3,1],[3,4]] → 2
// mat = [[1,1],[1,1]] → 1
// mat = [[3,1,6],[-9,5,7]] → 4
//
// Improvements
// - If values were dense integers, counting sort / radix could replace sorting keys — rarely needed here.
//
// --- end notes ---
//
// @lc code=start

import "sort"

type _pos2713 struct {
	i, j int
}

// MaxIncreasingCells2713 returns the maximum length of a strictly-increasing walk
// by moves within the same row or column.
func MaxIncreasingCells2713(mat [][]int) int {
	m, n := len(mat), len(mat[0])
	buckets := make(map[int][]_pos2713, m*n)
	for i := 0; i < m; i++ {
		for j := 0; j < n; j++ {
			v := mat[i][j]
			buckets[v] = append(buckets[v], _pos2713{i: i, j: j})
		}
	}

	keys := make([]int, 0, len(buckets))
	for v := range buckets {
		keys = append(keys, v)
	}
	sort.Ints(keys)

	rowMax := make([]int, m)
	colMax := make([]int, n)
	ans := 0

	for _, v := range keys {
		pos := buckets[v]
		mx := make([]int, len(pos))
		for k, p := range pos {
			bestPrev := rowMax[p.i]
			if colMax[p.j] > bestPrev {
				bestPrev = colMax[p.j]
			}
			mx[k] = bestPrev + 1
			if mx[k] > ans {
				ans = mx[k]
			}
		}
		for k, p := range pos {
			if mx[k] > rowMax[p.i] {
				rowMax[p.i] = mx[k]
			}
			if mx[k] > colMax[p.j] {
				colMax[p.j] = mx[k]
			}
		}
	}

	return ans
}

// @lc code=end

