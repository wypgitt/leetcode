//
// @lc app=leetcode id=1125 lang=python3
//
// [1125] Smallest Sufficient Team
//
//
// --- Interview notes (bitmask model, DP over subsets, reconstruction, complexity, edges, tests) ---
//
// Problem
// Map required skills to indices 0..m-1. Each person covers a subset of those skills. Choose the smallest number of
// people such that their union of skills is all required skills (each skill appears in at least one chosen person).
// Return any optimal team as person indices.
//
// Why bitmask state compression
// m = len(req_skills) <= 16 → at most 2^m distinct subsets of skills. Represent subset as integer mask:
// bit i is 1 iff skill i is covered by the team built so far.
//
// Person bitmask
// For person j, p[j] ORs bits for skills they know (only req_skills strings appear in input).
//
// DP definition
// f[mask] = minimum team size that achieves exactly the covered-skill set mask (subset of required skills).
// Transition: from state mask, adding person j moves to new_mask = mask | p[j] with team size + 1.
// Relaxation: if f[mask] + 1 < f[new_mask], update f[new_mask], record last person g[new_mask] = j and previous
// mask h[new_mask] = mask for reconstruction.
//
// Initialization
// f[0] = 0 (empty team covers no skill); all other f entries set to +infinity (unreachable).
//
// Iteration order (editorial loop)
// Enumerate every mask i from 0 .. 2^m-1; skip unreachable masks. For each person j, try relaxing edge i → i | p[j].
// Visiting masks in increasing integer order still propagates correctly because later masks inherit shorter paths as
// soon as their predecessors become finite (effectively BFS-like layering on augmented graph — equivalent relaxation).
//
// Reconstruction
// Start at full mask target = 2^m - 1. Repeatedly append g[target], then target ← h[target], until target == 0.
//
// Why not greedy by skill frequency
// Counterexamples exist — subset interaction requires DP / exhaustive search over exponential skill states (bounded
// by m ≤ 16).
//
// Time complexity
// O(2^m · n) relaxations; reconstruction O(team size) ≤ O(m).
//
// Space complexity
// O(2^m) arrays f, g, h plus O(n) person masks.
//
// Edge cases
// One skill, one person covering it — answer single index.
// Problem guarantees feasibility so full mask is reachable.
//
// Tests (statement)
// Example teams may appear in any order / alternate optimal indices — both [0,2] and [2,0] valid for Example 1.
//
// Improvements
// • Store only parent pointer + last person without copying lists — already done with g/h.
// • If tie-breaking among equal-size teams matters (not required here), prefer lexicographic smallest index lists —
//   would adjust `<` to tie-break on transitions.
//
// --- end notes ---
//
// @lc code=start

package leetcode

func SmallestSufficientTeam1125(reqSkills []string, people [][]string) []int {
	sid := make(map[string]int, len(reqSkills))
	for i, s := range reqSkills {
		sid[s] = i
	}
	m := len(reqSkills)
	n := len(people)

	p := make([]int, n)
	for i, skills := range people {
		mask := 0
		for _, s := range skills {
			if idx, ok := sid[s]; ok {
				mask |= 1 << idx
			}
		}
		p[i] = mask
	}

	inf := 1 << 30
	size := 1 << m
	f := make([]int, size)
	g := make([]int, size)
	h := make([]int, size)
	for i := 1; i < size; i++ {
		f[i] = inf
	}

	for mask := 0; mask < size; mask++ {
		if f[mask] == inf {
			continue
		}
		for j := 0; j < n; j++ {
			nm := mask | p[j]
			if f[mask]+1 < f[nm] {
				f[nm] = f[mask] + 1
				g[nm] = j
				h[nm] = mask
			}
		}
	}

	full := size - 1
	ans := make([]int, 0, f[full])
	cur := full
	for cur != 0 {
		ans = append(ans, g[cur])
		cur = h[cur]
	}
	return ans
}

// @lc code=end

