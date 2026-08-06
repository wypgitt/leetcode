package leetcode

import "sort"

//
// LeetCode 2589 — Minimum Time to Complete All Tasks
//
// --- Notes (problem, greedy idea, correctness sketch, DS, complexity, tests, edges, interview) ---
//
// Problem restatement
// Each task i is [start_i, end_i, duration_i] with integer time on a line (seconds / slots).
// You must schedule time slots when the machine is ON so that task i runs for duration_i
// seconds, and all those seconds lie inside the CLOSED interval [start_i, end_i].
// Many tasks may share the same second (parallelism). When idle, the machine can be off.
// Minimize the total number of distinct seconds the machine is ON (equivalently: minimize the
// cardinality of the set of chosen integer time points).
//
// Why greedy + “as late as possible” works (intuition)
// Think of each chosen second as a reusable token inside any task interval that contains it.
// Process tasks in increasing order of end_i. For the current task, some tokens may already
// exist in [start_i, end_i] from earlier choices (which only involved tasks that ended no later
// than current end_i). Use those first — they are “free” toward duration_i.
// Any remaining required seconds should be placed as LATE as possible inside [start_i, end_i],
// i.e. starting from end_i and walking left, picking unused slots. Late placement keeps earlier
// slots free for future tasks whose intervals may extend further right; this matches the standard
// exchange argument for interval scheduling / minimum points to hit interval demands.
//
// Algorithm
// 1) Sort tasks by end_i ascending.
// 2) Maintain a boolean array `on[t]` (or a set) meaning “second t is already used”.
// 3) For each [start, end, duration]:
//    - already = number of t in [start, end] with on[t] True.
//    - need = duration - already (may be 0).
//    - While need > 0: scan t = end, end-1, ... ; if not on[t], set on[t] = True and need -= 1.
// 4) Answer = total count of True in `on` (number of seconds machine was on).
//
// Data structures
// - Boolean array indexed by time: O(1) mark / query per slot; constraints keep time axis bounded
//   (LeetCode: end_i <= 2000), so array size ~2001 is O(1) extra space.
// - Alternative: a Python set of occupied seconds — same asymptotics, slightly more overhead per op.
//
// Time complexity
// - Sorting: O(n log n) for n tasks.
// - Per task: counting occupied slots in [start, end] is O(end - start + 1) <= O(U) where U is max time.
// - Filling from the right: each second is turned on at most once globally, but the backward scan
//   may skip already-on slots; worst-case work per task is O(U), so overall O(n * U).
// With U = 2000 constant, this is effectively O(n) up to a fixed factor.
//
// Space complexity
// - O(U) for the boolean timeline, O(1) relative to problem’s fixed coordinate bound.
//
// Edge cases
// - Tasks fully covered by prior slots: need = 0, no new seconds.
// - duration equals window length: may need every second in [start, end] if no overlap help.
// - All tasks share one heavy overlap window: greedy still fills from the right per task order by end.
//
// Tests (conceptual)
// - Single task [0, 5, 3]: place 3 latest slots e.g. 5,4,3 -> 3 seconds on.
// - Two disjoint intervals: each needs its own slots; sum of demands unless overlap allows sharing.
//
// Improvements
// - If U were huge (not here), use a balanced BST / interval union structure instead of a dense array.
// - Prefix sums on `on` for faster range counts if range queries dominated (same U bound here).
//
// LeetCode submission note
// Imports must live inside # @lc code=start ... end — otherwise NameError on List at submit time.
//
// Interview walkthrough
// 1) Reframe as minimizing distinct chosen integers on a timeline with per-interval multiplicity.
// 2) Argue processing by increasing end time + taking latest free slots is optimal (exchange / greedy).
// 3) Implement with a timeline bitset/bool array; analyze U constant from constraints.
// 4) Mention parallelism => reuse seconds across tasks; proof sketch via reordering chosen slots.
// --- end notes ---
//

// FindMinimumTime2589 returns the minimum number of seconds the machine must be on.
func FindMinimumTime2589(tasks [][]int) int {
	maxEnd := 0
	for _, t := range tasks {
		if t[1] > maxEnd {
			maxEnd = t[1]
		}
	}
	on := make([]bool, maxEnd+1)

	sort.Slice(tasks, func(i, j int) bool { return tasks[i][1] < tasks[j][1] })

	for _, task := range tasks {
		start, end, duration := task[0], task[1], task[2]
		already := 0
		for t := start; t <= end; t++ {
			if on[t] {
				already++
			}
		}
		need := duration - already
		t := end
		for need > 0 {
			if !on[t] {
				on[t] = true
				need--
			}
			t--
		}
	}

	ans := 0
	for _, v := range on {
		if v {
			ans++
		}
	}
	return ans
}

