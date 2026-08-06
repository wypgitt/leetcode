//
// @lc app=leetcode id=3892 lang=python3
//
// [3892] Minimum Operations to Achieve at Least K Peaks
//
//
// @lc code=start
// class Solution:
//     pass
//
//
// @lc code=end
//
// #
// @lc app=leetcode id=3892 lang=python3
//
// [3892] Minimum Operations to Achieve At Least K Peaks
//
// --- Notes (problem restatement, feasibility, greedy + heap, complexity, interview) ---
//
// Problem restatement
// Circular array nums[0..n-1]. Index i is a PEAK iff nums[i] is strictly greater than
// both neighbors (indices wrap: neighbor of 0 is n-1 and 1).
// Operation: pick any i and increase nums[i] by 1 (any number of times).
// Goal: minimum total operations so that the array has AT LEAST k peaks.
// If impossible, return -1.
//
// Feasibility (how many peaks can exist?)
// Two adjacent indices cannot both be peaks (would require nums[i] > nums[i+1] and
// nums[i+1] > nums[i]). On a cycle, peaks form an independent set of the cycle graph C_n.
// Maximum size of an independent set on C_n is floor(n/2). So if k > floor(n/2),
// impossible. Equivalently: if 2*k > n, return -1 (same integer test used below).
// Edge: k == 0 -> answer 0 with no operations.
//
// Why greedy + heap works (high level)
// Only increases are allowed. To make index i a peak with CURRENT neighbor values
// (still at their placement in the evolving circular list), the cheapest target height is
// max(nums[left], nums[right]) + 1, so cost_i = max(0, that_target - nums[i]).
// We repeatedly choose a remaining index i with MINIMUM marginal cost among indices that
// can still become peaks (not blocked). After committing index i as a peak, its two
// neighbors can never be peaks, so we remove them from consideration and MERGE the ring:
// node i becomes the representative of a merged arc; its updated cost uses the
// inclusion-exclusion merge:
//   new_cost[i] = cost[left[i]] + cost[right[i]] - cost[i]
// (left/right refer to the doubly-linked predecessor/successor on the circle BEFORE the
// merge step). This matches known contest implementations for this problem.
//
// Data structures
// - lookup[i]: index i cannot be chosen as a peak (neighbor of a chosen peak).
// - Doubly linked list on the cycle: left[i], right[i] point to prev/next alive nodes.
//   After picking peak i, neighbors are blocked; i bridges left[left[i]] and right[right[i]].
// - Min-heap of (cost[i], i) for lazy updates; stale entries skipped via lookup.
//
// Relation to official hints (DP)
// LeetCode hints describe casework (whether index 0 / n-1 is a peak) and dp[i][j] on a
// prefix — a valid alternate solution. This file implements the greedy + heap approach,
// which is O(n log n) and matches reference solutions (e.g. kamyu104) and brute checks on
// small n for random data.
//
// Time complexity
// Each heap push/pop is O(log n). Each accepted peak does O(1) pointer surgery and one
// push; stale pops add extra work but total pushes bounded by O(n + k). Worst-case
// ~ O((n + k) log n), fine for n <= 5000.
//
// Space complexity
// O(n) for arrays + heap.
//
// Edge cases
// - k == 0: return 0 immediately.
// - 2*k > n: impossible (more peaks than max independent set on C_n).
// - After loop, if fewer than k peaks taken (should not happen when feasible), return -1.
//
// Tests (statement examples)
// [2,1,2], k=1 -> raise nums[2] to 3 => cost 1.
// [4,5,3,6], k=2 -> already two peaks at 1 and 3 => 0.
// [3,7,3], k=2 -> max one peak on C_3 => -1.
//
// Possible improvements / variants
// - Implement digit-style DP from hints if you need to avoid floating merge intuition.
// - Store heap as list of unique indices with decrease-key if Python allowed — current
//   lazy heap is standard.
// --- end notes ---
//
// @lc code=start
// import heapq
//
//
// class Solution:
//     def minOperations(self, nums: list[int], k: int) -> int:
//         n = len(nums)
//         if k == 0:
//             return 0
//         if 2 * k > n:
//             return -1
//
//         lookup = [False] * n
//         left = [(i - 1) % n for i in range(n)]
//         right = [(i + 1) % n for i in range(n)]
//         cost = [
//             max(max(nums[left[i]], nums[right[i]]) + 1 - nums[i], 0) for i in range(n)
//         ]
//
//         heap: list[tuple[int, int]] = [(cost[i], i) for i in range(n)]
//         heapq.heapify(heap)
//
//         result = 0
//         remaining = k
//
//         while heap:
//             c, i = heapq.heappop(heap)
//             if lookup[i]:
//                 continue
//             result += c
//             remaining -= 1
//             if remaining == 0:
//                 return result
//
//             cost[i] = cost[left[i]] + cost[right[i]] - cost[i]
//             heapq.heappush(heap, (cost[i], i))
//
//             lookup[left[i]] = True
//             lookup[right[i]] = True
//
//             left[i] = left[left[i]]
//             right[i] = right[right[i]]
//             right[left[i]] = i
//             left[right[i]] = i
//
//         return -1
//
//
// @lc code=end
//
package leetcode

//
// @lc app=leetcode id=3892 lang=golang
//
// [3892] Minimum Operations to Achieve At Least K Peaks
//

// --- Notes (problem restatement, feasibility, greedy + heap, complexity, interview) ---
//
// Problem restatement
// Circular array nums[0..n-1]. Index i is a PEAK iff nums[i] is strictly greater than
// both neighbors (indices wrap: neighbor of 0 is n-1 and 1).
// Operation: pick any i and increase nums[i] by 1 (any number of times).
// Goal: minimum total operations so that the array has AT LEAST k peaks.
// If impossible, return -1.
//
// Feasibility (how many peaks can exist?)
// Two adjacent indices cannot both be peaks (would require nums[i] > nums[i+1] and
// nums[i+1] > nums[i]). On a cycle, peaks form an independent set of the cycle graph C_n.
// Maximum size of an independent set on C_n is floor(n/2). So if k > floor(n/2),
// impossible. Equivalently: if 2*k > n, return -1 (same integer test used below).
// Edge: k == 0 -> answer 0 with no operations.
//
// Why greedy + heap works (high level)
// Only increases are allowed. To make index i a peak with CURRENT neighbor values
// (still at their placement in the evolving circular list), the cheapest target height is
// max(nums[left], nums[right]) + 1, so cost_i = max(0, that_target - nums[i]).
// We repeatedly choose a remaining index i with MINIMUM marginal cost among indices that
// can still become peaks (not blocked). After committing index i as a peak, its two
// neighbors can never be peaks, so we remove them from consideration and MERGE the ring:
// node i becomes the representative of a merged arc; its updated cost uses the
// inclusion-exclusion merge:
//   new_cost[i] = cost[left[i]] + cost[right[i]] - cost[i]
// (left/right refer to the doubly-linked predecessor/successor on the circle BEFORE the
// merge step). This matches known contest implementations for this problem.
//
// Data structures
// - lookup[i]: index i cannot be chosen as a peak (neighbor of a chosen peak).
// - Doubly linked list on the cycle: left[i], right[i] point to prev/next alive nodes.
//   After picking peak i, neighbors are blocked; i bridges left[left[i]] and right[right[i]].
// - Min-heap of (cost[i], i) for lazy updates; stale entries skipped via lookup.
//
// Relation to official hints (DP)
// LeetCode hints describe casework (whether index 0 / n-1 is a peak) and dp[i][j] on a
// prefix — a valid alternate solution. This file implements the greedy + heap approach,
// which is O(n log n) and matches reference solutions (e.g. kamyu104) and brute checks on
// small n for random data.
//
// Time complexity
// Each heap push/pop is O(log n). Each accepted peak does O(1) pointer surgery and one
// push; stale pops add extra work but total pushes bounded by O(n + k). Worst-case
// ~ O((n + k) log n), fine for n <= 5000.
//
// Space complexity
// O(n) for arrays + heap.
//
// Edge cases
// - k == 0: return 0 immediately.
// - 2*k > n: impossible (more peaks than max independent set on C_n).
// - After loop, if fewer than k peaks taken (should not happen when feasible), return -1.
//
// Tests (statement examples)
// [2,1,2], k=1 -> raise nums[2] to 3 => cost 1.
// [4,5,3,6], k=2 -> already two peaks at 1 and 3 => 0.
// [3,7,3], k=2 -> max one peak on C_3 => -1.
//
// Possible improvements / variants
// - Implement digit-style DP from hints if you need to avoid floating merge intuition.
// - Store heap as list of unique indices with decrease-key if Python allowed — current
//   lazy heap is standard.
// --- end notes ---

// @lc code=start

import (
	"container/heap"
)

type peakHeap3892 []*peakItem3892

type peakItem3892 struct {
	cost int
	idx  int
}

func (h peakHeap3892) Len() int { return len(h) }

func (h peakHeap3892) Less(i, j int) bool {
	if h[i].cost != h[j].cost {
		return h[i].cost < h[j].cost
	}
	return h[i].idx < h[j].idx
}

func (h peakHeap3892) Swap(i, j int) { h[i], h[j] = h[j], h[i] }

func (h *peakHeap3892) Push(x interface{}) {
	*h = append(*h, x.(*peakItem3892))
}

func (h *peakHeap3892) Pop() interface{} {
	old := *h
	n := len(old)
	x := old[n-1]
	*h = old[:n-1]
	return x
}

// MinOperations3892 returns minimum increments to achieve at least k peaks on the circular array.
func MinOperations3892(nums []int, k int) int {
	n := len(nums)
	if k == 0 {
		return 0
	}
	if 2*k > n {
		return -1
	}

	lookup := make([]bool, n)
	left := make([]int, n)
	right := make([]int, n)
	for i := 0; i < n; i++ {
		left[i] = (i - 1 + n) % n
		right[i] = (i + 1) % n
	}

	cost := make([]int, n)
	for i := 0; i < n; i++ {
		need := max3892(nums[left[i]], nums[right[i]]) + 1 - nums[i]
		if need < 0 {
			need = 0
		}
		cost[i] = need
	}

	h := &peakHeap3892{}
	heap.Init(h)
	for i := 0; i < n; i++ {
		heap.Push(h, &peakItem3892{cost: cost[i], idx: i})
	}

	result := 0
	remaining := k

	for h.Len() > 0 {
		it := heap.Pop(h).(*peakItem3892)
		c, i := it.cost, it.idx
		if lookup[i] {
			continue
		}
		result += c
		remaining--
		if remaining == 0 {
			return result
		}

		cost[i] = cost[left[i]] + cost[right[i]] - cost[i]
		heap.Push(h, &peakItem3892{cost: cost[i], idx: i})

		lookup[left[i]] = true
		lookup[right[i]] = true

		left[i] = left[left[i]]
		right[i] = right[right[i]]
		right[left[i]] = i
		left[right[i]] = i
	}

	return -1
}

func max3892(a, b int) int {
	if a > b {
		return a
	}
	return b
}

// @lc code=end
