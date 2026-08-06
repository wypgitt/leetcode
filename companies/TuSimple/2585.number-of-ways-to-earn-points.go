package leetcode

//
// LeetCode 2585 — Number of Ways to Earn Points
//
// --- Notes (problem, modeling, DP, complexity, modulo, tests, edges, improvements, interview) ---
//
// Problem restatement
// You need exactly `target` points. There are several QUESTION TYPES. Type i is described by
//   types[i] = [count_i, marks_i]:
//   - there are count_i distinct questions of that type (solve each at most once),
//   - each solved question of that type awards marks_i points.
// Count how many different subsets / choices of questions produce a TOTAL score of exactly
// `target`. Two ways differ if a different multiset of questions is solved (which question indices
// matter only through type and whether it is chosen within its budget).
// Return the count modulo 1_000_000_007.
//
// Modeling (combinatorial object)
// For each type i, choose an integer k_i = how many questions of that type you solve, with
//   0 <= k_i <= count_i. Each contributes k_i * marks_i points.
// A feasible plan satisfies sum_i k_i * marks_i = target.
// The problem counts HOW MANY such vectors (k_1,...,k_n) exist — one way per distinct tuple.
// (Questions within a type are treated as identical except quantity; we do not multiply by C(count_i, k_i).)
//
// Algorithm choice — dynamic programming (bounded knapsack COUNTING)
// This is the “bounded knapsack” variant where each item type i has weight marks_i, at most count_i
// copies, and we count the number of ways to achieve EXACT total weight = target (not minimize cost).
// Order of processing types does not matter for existence of a composition; we build DP over types
// sequentially to avoid overcounting (same multiset counted once).
//
// State
// dp[j] = number of ways to reach exactly j points using ONLY the types processed so far.
//
// Transition (process one type [cnt, w])
// From previous array prev, build next:
//   next_dp[j] = sum_{k=0}^{min(cnt, floor(j/w))} prev[j - k*w]
// Interpretation: pick k questions of this type (each worth w), contributing k*w points; previous
// types must contribute the remainder j - k*w.
//
// Initialization: dp[0] = 1 (empty selection / zero points); dp[j>0] = 0 before any type.
// Answer: dp[target] after all types are merged.
//
//
// Implementation structure
// Use two 1D arrays of length target+1 (or one array with careful layering — easier to use prev /
// cur each layer). For clarity we allocate `cur` each type; space can be halved by reusing buffers.
//
// Time complexity
// For each of T types, for each j in 0..target, inner k runs up to min(cnt, j/w) ~ O(target/w * cnt)
// worst-case naive triple loop O(types * target * max(cnt)).
// With typical LC bounds (target <= 1000, small counts) this passes easily.
//
// Space complexity
// O(target) for one DP row (two rows if using prev/cur explicitly).
//
// Modulo arithmetic
// Every addition uses % MOD to prevent overflow and match required modulus.
// Implementation detail: define MOD inside waysToReachTarget — LeetCode only submits code between
// @lc code=start/end, so a module-level MOD would be stripped and cause NameError on submit time.
//
// Edge cases
// - target == 0: exactly one way — choose no questions from every type (dp[0] stays 1).
// - Impossible target: answer 0.
// - Large marks: inner loop guard k <= j // w prevents invalid indices.
//
// Tests (examples)
// - target = 6, types = [[6,1],[3,2],[2,3]] -> 7 (standard editorial example).
// - target = 0 -> 1 (choose no questions).
// - Single type [5, 2], target 6 -> k = 3 allowed -> 1 way.
//
// Improvements (same asymptotics better constants)
// - Sliding-window / prefix-sum optimization per residue class modulo w reduces inner k-loop to
//   amortized O(1) per j -> O(types * target) time when counts are large (classic bounded knapsack
//   optimization).
// - In-place rolling array only if transition rewritten safely (bounded knapsack usually uses layer
//   separation — easier with prev/cur).
//
// Interview walkthrough
// 1) Recognize counting compositions with per-variable caps -> bounded knapsack counting.
// 2) Define dp[j] over processed prefixes of types; argue no double counting (ordered extension).
// 3) Transition summing over k copies of current weight w.
// 4) Complexity and modulo; mention sliding-window upgrade if interviewer pushes constraints.
// --- end notes ---
//

// WaysToReachTarget2585 returns number of ways to reach target points modulo 1e9+7.
func WaysToReachTarget2585(target int, types [][]int) int {
	const MOD = 1_000_000_007
	prev := make([]int, target+1)
	prev[0] = 1
	for _, t := range types {
		cnt, w := t[0], t[1]
		cur := make([]int, target+1)
		for j := 0; j <= target; j++ {
			upto := cnt
			if j/w < upto {
				upto = j / w
			}
			acc := 0
			for k := 0; k <= upto; k++ {
				acc += prev[j-k*w]
				if acc >= MOD {
					acc -= MOD
				}
			}
			cur[j] = acc
		}
		prev = cur
	}
	return prev[target] % MOD
}

