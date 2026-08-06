//
// @lc app=leetcode id=2709 lang=python3
//
// [2709] Greatest Common Divisor Traversal
//

// --- Interview notes (graph model, DSU on primes, complexity, edges, tests) ---
//
// Problem
// Indices i and j are adjacent iff gcd(nums[i], nums[j]) > 1. Determine whether the graph on
// {0..n-1} is connected (every pair reachable by a path).
//
// Why not build edges between all pairs
// n up to 1e5 — O(n^2) edges is impossible. gcd(a,b)>1 iff a and b share a prime factor. So connectivity
// is determined by shared primes — we only need to link numbers that share at least one prime.
//
// Graph reformulation (standard trick)
// Build a bipartite-style union structure:
//   - Left side: index nodes 0 .. n-1.
//   - Right side: one node per possible prime p ∈ [2, max(nums)] (IDs we’ll offset by n).
// Connect index i with every prime p that divides nums[i]. Then two indices share a prime p iff both are
// attached to the same prime node p, hence they lie in the same connected component of this union graph.
// Formally: index i is merged with node (n + p) for each prime p | nums[i]. Transitive closure of unions
// equals connectivity of the original gcd graph.
//
// Prime factors per value
// Precompute distinct prime factors for each x in [1, MX] using trial division up to √x (MX = 1e5 per
// constraints). nums[i] == 1 has no prime factors → that index gets no edges via primes (isolated unless n
// is 1).
//
// Data structures
// - Disjoint Set Union (Union-Find) with path compression + union by size: nearly O(α(N)) per op.
// - Static table `PF[x]` = list of distinct primes dividing x.
//
// Algorithm
// 1. If len(nums) == 1: return True (single vertex is trivially “connected”).
// 2. Let m = max(nums); allocate DSU of size n + m + 1 (index nodes 0..n-1, prime p uses node id n+p).
// 3. For each i, for each prime p in PF[nums[i]], union(i, n + p).
// 4. Return True iff all indices 0..n-1 share one root (e.g. find(0) == find(i) for all i, or count roots).
//
// Time complexity
// - Precompute PF once: O(MX · √MX) ≈ O(MX^1.5) trial division; acceptable for MX = 1e5 at startup / once.
// - Per query / each call: O(n · ω(nums[i])) unions where ω is number of distinct prime factors (small),
//   plus DSU α inverse ackermann — dominated by precompute + O(n log MAX) loose bound.
// Space: O(MX) for PF table + O(n + m) for DSU.
//
// Edge cases
// - nums = [1]: True (one node).
// - nums contains 1 with other values > 1: index with value 1 never unions with primes → cannot leave that
//   component unless n == 1 → typically False (except edge cases where graph still connects via others — but 1
//   shares gcd 1 with everyone, so no edges from that index).
// - nums = [1, 1]: gcd(1,1)=1 → no edge → False.
// - All nums share a prime through a chain (Example 1): DSU merges into one component.
//
// Tests (statement)
// [2,3,6] → True; [3,9,5] → False; [4,3,12,8] → True.
//
// Improvements
// - Linear sieve + smallest prime factor (SPF) array yields faster factorization per nums[i] if many queries.
// - Could lazy-init PF table only if Solution called multiple times — LeetCode calls once per instance.
//
// --- end notes ---
//
// @lc code=start

package leetcode

//
// @lc app=leetcode id=2709 lang=golang
//
// [2709] Greatest Common Divisor Traversal
//
// --- Interview notes (graph model, DSU on primes, complexity, edges, tests) ---
//
// Problem
// Indices i and j are adjacent iff gcd(nums[i], nums[j]) > 1. Determine whether the graph on
// {0..n-1} is connected (every pair reachable by a path).
//
// Why not build edges between all pairs
// n up to 1e5 — O(n^2) edges is impossible. gcd(a,b)>1 iff a and b share a prime factor. So connectivity
// is determined by shared primes — we only need to link numbers that share at least one prime.
//
// Graph reformulation (standard trick)
// Build a bipartite-style union structure:
//   - Left side: index nodes 0 .. n-1.
//   - Right side: one node per possible prime p ∈ [2, max(nums)] (IDs we’ll offset by n).
// Connect index i with every prime p that divides nums[i]. Then two indices share a prime p iff both are
// attached to the same prime node p, hence they lie in the same connected component of this union graph.
// Formally: index i is merged with node (n + p) for each prime p | nums[i]. Transitive closure of unions
// equals connectivity of the original gcd graph.
//
// Prime factors per value
// Precompute distinct prime factors for each x in [1, MX] using trial division up to √x (MX = 1e5 per
// constraints). nums[i] == 1 has no prime factors → that index gets no edges via primes (isolated unless n
// is 1).
//
// Data structures
// - Disjoint Set Union (Union-Find) with path compression + union by size: nearly O(α(N)) per op.
// - Static table `PF[x]` = list of distinct primes dividing x.
//
// Algorithm
// 1. If len(nums) == 1: return True (single vertex is trivially “connected”).
// 2. Let m = max(nums); allocate DSU of size n + m + 1 (index nodes 0..n-1, prime p uses node id n+p).
// 3. For each i, for each prime p in PF[nums[i]], union(i, n + p).
// 4. Return True iff all indices 0..n-1 share one root (e.g. find(0) == find(i) for all i, or count roots).
//
// Time complexity
// - Precompute PF once: O(MX · √MX) ≈ O(MX^1.5) trial division; acceptable for MX = 1e5 at startup / once.
// - Per query / each call: O(n · ω(nums[i])) unions where ω is number of distinct prime factors (small),
//   plus DSU α inverse ackermann — dominated by precompute + O(n log MAX) loose bound.
// Space: O(MX) for PF table + O(n + m) for DSU.
//
// Edge cases
// - nums = [1]: True (one node).
// - nums contains 1 with other values > 1: index with value 1 never unions with primes → cannot leave that
//   component unless n == 1 → typically False (except edge cases where graph still connects via others — but 1
//   shares gcd 1 with everyone, so no edges from that index).
// - nums = [1, 1]: gcd(1,1)=1 → no edge → False.
// - All nums share a prime through a chain (Example 1): DSU merges into one component.
//
// Tests (statement)
// [2,3,6] → True; [3,9,5] → False; [4,3,12,8] → True.
//
// Improvements
// - Linear sieve + smallest prime factor (SPF) array yields faster factorization per nums[i] if many queries.
// - Could lazy-init PF table only if Solution called multiple times — LeetCode calls once per instance.
//
// --- end notes ---
//
// @lc code=start

const _mx2709 = 100_000

var _spf2709 []int

func init() {
	_spf2709 = make([]int, _mx2709+1)
	for i := 2; i <= _mx2709; i++ {
		if _spf2709[i] == 0 {
			_spf2709[i] = i
			if i*i <= _mx2709 {
				for j := i * i; j <= _mx2709; j += i {
					if _spf2709[j] == 0 {
						_spf2709[j] = i
					}
				}
			}
		}
	}
	_spf2709[1] = 1
}

type _dsu2709 struct {
	p  []int
	sz []int
}

func _newDSU2709(n int) *_dsu2709 {
	p := make([]int, n)
	sz := make([]int, n)
	for i := 0; i < n; i++ {
		p[i] = i
		sz[i] = 1
	}
	return &_dsu2709{p: p, sz: sz}
}

func (d *_dsu2709) find(x int) int {
	for d.p[x] != x {
		d.p[x] = d.p[d.p[x]]
		x = d.p[x]
	}
	return x
}

func (d *_dsu2709) union(a, b int) {
	pa, pb := d.find(a), d.find(b)
	if pa == pb {
		return
	}
	if d.sz[pa] < d.sz[pb] {
		pa, pb = pb, pa
	}
	d.p[pb] = pa
	d.sz[pa] += d.sz[pb]
}

func _distinctPrimeFactors2709(x int) []int {
	if x <= 1 {
		return nil
	}
	res := make([]int, 0, 4)
	for x > 1 {
		p := _spf2709[x]
		if p == 0 {
			p = x
		}
		res = append(res, p)
		for x%p == 0 {
			x /= p
		}
	}
	return res
}

// CanTraverseAllPairs2709 returns whether the gcd graph over indices is connected.
func CanTraverseAllPairs2709(nums []int) bool {
	n := len(nums)
	if n == 1 {
		return true
	}

	m := 0
	for _, x := range nums {
		if x > m {
			m = x
		}
	}
	uf := _newDSU2709(n + m + 1)

	for i, x := range nums {
		for _, p := range _distinctPrimeFactors2709(x) {
			uf.union(i, n+p)
		}
	}

	root := uf.find(0)
	for i := 1; i < n; i++ {
		if uf.find(i) != root {
			return false
		}
	}
	return true
}

// @lc code=end

