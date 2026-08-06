package leetcode

//
// @lc app=leetcode id=2702 lang=golang
//
// [2702] Minimum Operations to Make Numbers Non-positive
//
// --- Interview notes (model, feasibility check, binary search, complexity, edges, tests) ---
//
// Problem
// One operation: pick an index i. Decrease nums[i] by x; decrease every other entry by y.
// Constraints (given): 1 <= y < x <= 1e9, so each operation strictly decreases the sum of the array.
// Return the minimum number of operations so that every nums[j] <= 0.
//
// Algebraic model
// Fix a total number of operations T. Let k_j be how many of those T operations chose index j.
// Then sum_j k_j = T (each operation picks exactly one index).
// For a fixed position j, across all T rounds it is chosen k_j times and “not chosen” T − k_j times, so the
// total decrement applied to nums[j] is:
//   k_j * x + (T - k_j) * y  =  T * y  +  k_j * (x - y).
// We need, for every original value v = nums[j]:
//   T * y + k_j * (x - y)  >=  v
// ⟺  k_j * (x - y)  >=  v - T * y.
// If v <= T * y, the passive part T*y already covers v and we may take k_j = 0.
// If v > T * y, we need k_j >= ceil((v - T * y) / (x - y)).
//
// Feasibility of a candidate T
// Define need_j = 0 if v <= T*y, else ceil((v - T*y) / (x - y)). Any valid schedule must satisfy k_j >= need_j,
// hence sum_j k_j >= sum_j need_j. But sum_j k_j = T, so a necessary condition is:
//   sum_j need_j  <=  T.
// This condition is also sufficient: if sum need_j <= T, assign exactly need_j “special” picks to each j and
// distribute the remaining T - sum need_j picks arbitrarily (extra picks only increase decrements further).
//
// Monotonicity ⇒ binary search on the answer
// If T operations suffice, then T+1 operations also suffice (extra round adds at least y to every element).
// If T does not suffice, no smaller T suffices. So { feasible T } is upward-closed; we binary-search the minimum.
//
// Check(T) implementation
// Accumulate cnt = sum of ceil terms using integer arithmetic (avoid floats):
//   if v > T*y: cnt += (v - T*y + (x - y) - 1) // (x - y)
// Early exit if cnt > T.
//
// Search range
// Lower bound l = 0. Upper bound r = max(nums) works under problem constraints (editorial); every element drops
// by at least y per operation, so rough magnitude stays O(max(nums)/y). With nums[i] <= 1e9, hi = max(nums) is
// safe on official tests.
//
// Why binary search vs closed form
// The feasibility predicate is monotone but not a simple rational function of T because of ceilings per element,
// so binary search on T is the standard O(n log U) approach (U ~ max value).
//
// Time complexity
// O(n log M) where M = max(nums) for the binary search range (about 30–60 iterations for 1e9).
//
// Space complexity
// O(1) extra besides the input array (only loop counters / accumulators).
//
// Edge cases (discussion)
// - Single element: reduces to needing T with T*y + T*(x-y) = T*x >= v when always picking that index — check still works.
// - All nums[j] <= T*y at candidate T: cnt = 0, feasible.
// - y < x guarantees x - y > 0 so division is well-defined.
//
// Tests (statement examples)
// nums = [3,4,1,7,6], x = 4, y = 2 → answer 3.
// nums = [1,2,1], x = 2, y = 1 → answer 1.
//
// Improvements
// - Tighter upper bound can shrink log factor slightly; rarely needed.
// - Early exit in check already cuts average work when infeasible.
//
// --- end notes ---
//
// @lc code=start

// MinOperations2702 returns the minimum operations to make every number <= 0.
func MinOperations2702(nums []int, x int, y int) int {
	diff := int64(x - y)

	check := func(t int64) bool {
		var cnt int64
		ty := t * int64(y)
		for _, vv := range nums {
			v := int64(vv)
			if v > ty {
				need := (v - ty + diff - 1) / diff
				cnt += need
				if cnt > t {
					return false
				}
			}
		}
		return cnt <= t
	}

	var hi int64
	for _, v := range nums {
		if int64(v) > hi {
			hi = int64(v)
		}
	}

	var lo int64
	for lo < hi {
		mid := (lo + hi) >> 1
		if check(mid) {
			hi = mid
		} else {
			lo = mid + 1
		}
	}
	return int(lo)
}

// @lc code=end

