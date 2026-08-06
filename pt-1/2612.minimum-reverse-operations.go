package leetcode

//
// @lc app=leetcode id=2612 lang=golang
//
// [2612] Minimum Reverse Operations
//
// --- Notes (problem, graph model, parity / interval, DSU skip, BFS, complexity, edges, interview) ---
//
// Problem restatement
// Length-n binary array (indices 0..n-1). Exactly one position `p` is 1; all others 0.
// One operation: choose any contiguous subarray of length exactly `k` and reverse it (the single 1
// moves with its element). After each operation, the 1 must NOT lie on any index in `banned`.
// For every index `i`, compute the minimum number of operations to have the 1 at `i`, or -1 if
// impossible. Return an array of length n (answer[p] is always 0).
//
// Graph modeling
// Positions 0..n-1 are states. An undirected edge connects u and v if one reverse of length k can
// send the 1 from u to v in one step (and v to u), while the landing position is not banned.
// All edges have weight 1 -> shortest path = minimum operations -> BFS from source `p`.
//
// Neighbor formula (reverse window [l, l+k-1] containing u)
// After reversing, index u maps to v = l + (l+k-1) - u = 2l + k - 1 - u.
// For fixed u and k, as l runs over integers such that 0 <= l <= n-k and l <= u <= l+k-1,
// we get l in [max(0,u-k+1), min(u, n-k)], and v = 2l + k - 1 - u steps by 2 when l increases by 1.
// So from u you can reach a contiguous range of candidate indices [L, R] that share the same
// parity pattern (step size 2 in index space).
//
// Reachable interval endpoints (equivalent forms appear in editorials)
// With walkccc / kamyu notation:
//   L = max(u - k + 1, k - 1 - u)
//   R = min(u + k - 1, n - 1 - (u - (n - k)))
// Any valid destination index v in one move lies in [L, R] with v ≡ L (mod 2).
//
// Why not naive BFS?
// A single u may have Theta(k) neighbors; dense edges make O(n*k) BFS too slow for large n.
// All neighbors in one move form an arithmetic progression with step 2 inside [L,R]. We must
// enumerate unvisited positions in that range quickly — either:
//   (A) Two ordered sets keyed by parity -> bisect/range delete -> O(log n) per operation, or
//   (B) Disjoint-set “union with next index” + jump pointers -> amortized near O(1) per position.
//
// Algorithm implemented — BFS + Union-Find skip (kamyu / editorial O(n α(n)))
// Maintain DSU over indices 0..n+1 with auxiliary array `right` merged on union:
//   Initially right[i] = i. Idea: indices with same parity link by union(i, i+2); after visiting
//   index x we union(x, x+2) so future iterations skip over filled positions along that parity chain.
// When expanding BFS layer from u:
//   Compute [L, R] for one-step reachable indices (same parity as L).
//   Let x = find_first_available(L) implemented as uf.right_set(L) (depends on DSU state).
//   While x <= R: relax x (if not banned, set answer and push to next layer); ALWAYS union(x, x+2)
//   to remove x from future scans; then x <- uf.right_set(x).
// Start: union(p, p+2) once so the starting slot is skipped like visited along its parity chain.
//
// Banned indices
// Never enqueue them as destinations; still union past them when scanning so we do not stall on
// forbidden cells (kamyu always unions each x encountered in [L,R], but only pushes when not banned).
//
// Time complexity
// - Each index is processed / skipped at most once per parity chain logic -> O(n α(n)) DSU work
//   plus O(n) BFS layers overall -> ~O(n α(n)) ≈ O(n) practically.
//
// Space complexity
// - O(n) for DSU parent/rank/right, answer array, banned flags, queue.
//
// Alternative
// - SortedList / TreeSet per parity: O(n log n), only standard library if you simulate with bisect
//   on sorted arrays is O(n) per delete worst case — not ideal; DSU skip is the LC-friendly choice.
//
// Edge cases
// - k == n: only full-array reverses; limited neighbors.
// - banned contains almost all indices: many -1 entries.
// - p banned is impossible per constraints (usually p not in banned).
//
// LeetCode submission
// Imports must be inside # @lc code=start ... end (otherwise NameError on List at submit).
//
// Interview walkthrough
// 1) Model positions as graph; unweighted shortest path -> BFS.
// 2) Derive neighbor range [L,R] and step-2 structure from reverse formula.
// 3) Accelerate range relaxation with DSU skip list or balanced sets.
// 4) Complexity and parity bookkeeping.
// --- end notes ---
//
// @lc code=start

type _UFRight struct {
	parent []int
	rank   []int
	right  []int
}

func _newUFRight(n int) *_UFRight {
	p := make([]int, n)
	rk := make([]int, n)
	rt := make([]int, n)
	for i := 0; i < n; i++ {
		p[i] = i
		rt[i] = i
	}
	return &_UFRight{parent: p, rank: rk, right: rt}
}

func (uf *_UFRight) find(x int) int {
	for uf.parent[x] != x {
		uf.parent[x] = uf.parent[uf.parent[x]]
		x = uf.parent[x]
	}
	return x
}

func (uf *_UFRight) union(x, y int) bool {
	px, py := uf.find(x), uf.find(y)
	if px == py {
		return false
	}
	if uf.rank[px] > uf.rank[py] {
		px, py = py, px
	}
	uf.parent[px] = py
	if uf.rank[px] == uf.rank[py] {
		uf.rank[py]++
	}
	if uf.right[px] > uf.right[py] {
		uf.right[py] = uf.right[px]
	}
	return true
}

func (uf *_UFRight) rightSet(x int) int {
	return uf.right[uf.find(x)]
}

func _maxInt2612(a, b int) int {
	if a > b {
		return a
	}
	return b
}

func _minInt2612(a, b int) int {
	if a < b {
		return a
	}
	return b
}

// MinReverseOperations2612 returns the minimum operations to move the single 1
// from p to every index using length-k reversals while never landing on banned indices.
func MinReverseOperations2612(n int, p int, banned []int, k int) []int {
	bannedOn := make([]bool, n)
	for _, x := range banned {
		if 0 <= x && x < n {
			bannedOn[x] = true
		}
	}

	ans := make([]int, n)
	for i := 0; i < n; i++ {
		ans[i] = -1
	}
	ans[p] = 0

	uf := _newUFRight(n + 2) // we may union with x+2 up to n+1
	uf.union(p, p+2)

	q := []int{p}
	step := 1
	for len(q) > 0 {
		next := make([]int, 0)
		for _, u := range q {
			left := _maxInt2612(u-k+1, k-1-u)
			right := _minInt2612(u+k-1, n-1-(u-(n-k)))

			x := uf.rightSet(left)
			for x <= right {
				if !bannedOn[x] && ans[x] == -1 {
					ans[x] = step
					next = append(next, x)
				}
				uf.union(x, x+2)
				x = uf.rightSet(x)
			}
		}
		q = next
		step++
	}

	return ans
}

// @lc code=end

