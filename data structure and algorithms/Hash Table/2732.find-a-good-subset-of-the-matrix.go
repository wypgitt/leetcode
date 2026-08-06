package leetcode

//
// @lc app=leetcode id=2732 lang=golang
//
// [2732] Find a Good Subset of the Matrix
//
// --- Interview notes (condition, bit trick, why only k=1 or 2, complexity, edges, tests) ---
//
// Problem
// Binary matrix m × n. Choose a non-empty subset of rows of size k. Let column sums be c_j.
// Require c_j <= floor(k / 2) for every column j.
// Return any sorted list of chosen row indices, or [] if impossible.
//
// Column semantics as bits
// Row i is a length-n bit pattern (n <= 5). Pack row into mask r_i ∈ [0, 2^n): bit j is grid[i][j].
//
// k = 1
// floor(1/2) = 0 ⇒ every column sum must be 0 ⇒ the row must be all zeros ⇒ mask == 0.
//
// k = 2
// floor(2/2) = 1 ⇒ each column sum ≤ 1 ⇒ no column may have two 1s ⇒ the two rows cannot both have a 1 in the
// same column ⇒ bitwise AND of their masks must be 0.
//
// Why larger k never helps (given n <= 5)
// - Odd k ≥ 3: floor(k/2) is still 1 (for k=3), same per-column cap as k=2. Any three rows contain a pair;
//   if no pair is disjoint (AND=0), triple cannot satisfy column sums ≤1 — editorial argues failure of k=2
//   implies failure for odd k>1.
// - Even k ≥ 4: floor(k/2) ≥ 2. Among any 4 distinct rows, there are C(4,2)=6 column pairs that could both be 1;
//   pushing sums above 2 forces some column sum ≥3 when n≤5 (pigeonhole / averaging argument in editorial).
// Therefore only k ∈ {1, 2} need to be checked.
//
// Algorithm
// 1. Scan rows; build mask per row. If mask == 0, immediately return [row_index].
// 2. Store map mask → row index (one representative index per distinct mask is enough: pairing masks A and B
//    only needs any row realizing A and any row realizing B).
// 3. For every pair of entries (a, i), (b, j) in the map, if (a & b) == 0, return sorted([i, j]).
// 4. Return [].
//
// Data structures
// - Dictionary / hash map from mask (int) to first-seen row index: O(2^n) distinct masks at most (here ≤ 32).
// - Bit operations for AND / packing row into mask.
//
// Time complexity
// O(m · n) to build masks + O(U^2) over distinct masks U ≤ 2^n ≤ 32 ⇒ effectively O(m · n + 4^n) with tiny constant.
//
// Space complexity
// O(U) for the map, O(1) besides input if masks streamed — here O(min(m, 2^n)) entries.
//
// Edge cases
// - Single cell [[0]]: mask 0 ⇒ [0].
// - Single cell [[1]]: no all-zero row; pairs need AND 0 — impossible with one row ⇒ []... Actually one row k=1:
//   need mask 0, [[1]] fails ⇒ [].
// - Duplicate identical rows: map keeps one index; pairing still finds disjoint masks from other rows if they exist.
//
// Tests (statement)
// Example 1 → [0,1]; Example 2 → [0]; Example 3 → [].
//
// Improvements
// - Iterate masks only up to 2^n without scanning all rows twice — current solution is already optimal order for
//   constraints.
//
// --- end notes ---
//
// @lc code=start

// GoodSubsetofBinaryMatrix2732 returns indices of a good subset of rows, or empty slice if impossible.
func GoodSubsetofBinaryMatrix2732(grid [][]int) []int {
	first := make(map[int]int, 32)
	for i, row := range grid {
		mask := 0
		for j, x := range row {
			if x != 0 {
				mask |= 1 << j
			}
		}
		if mask == 0 {
			return []int{i}
		}
		// Any representative index is fine.
		first[mask] = i
	}

	masks := make([]int, 0, len(first))
	for m := range first {
		masks = append(masks, m)
	}

	for _, a := range masks {
		for _, b := range masks {
			if (a & b) == 0 {
				i, j := first[a], first[b]
				if i < j {
					return []int{i, j}
				}
				return []int{j, i}
			}
		}
	}
	return nil
}

// @lc code=end

