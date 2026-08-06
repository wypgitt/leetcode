package leetcode

//
// @lc app=leetcode id=2646 lang=golang
//
// [2646] Minimize the Total Price of the Trips
//
// --- Notes (problem, path counts, tree DP, independence, complexity, edges, interview) ---
//
// Problem restatement
// Undirected tree on n nodes with integer prices price[u]. You are given several trips [start, end];
// each trip walks along the unique simple path between those endpoints (standard on a tree).
// For each node u, every time a trip path goes through u, you pay price[u] toward that trip’s
// contribution — equivalently, total cost equals sum_u price[u] * freq[u], where freq[u] is how
// many trip-paths include u.
// Before counting trips, you may choose a set of nodes whose prices are HALVED (integer division)
// for every traversal payment through them, with the rule that you cannot halve two adjacent nodes.
// Minimize the resulting total cost over all trips combined.
//
// Step 1 — frequency on paths (why not multiply per trip naïvely?)
// Each trip’s path is unique in a tree. For each [start, end], increment freq[u] by 1 for every u
// on that path. Implementation: DFS from start toward end by exploring neighbors except parent until
// hitting end; accumulate visited nodes on the successful branch (short-circuit once end found).
// Complexity O(sum of path lengths) <= O(n * |trips|) worst case; acceptable for LC constraints.
// Improvement: LCA + difference-on-tree marks all paths in O((n + |trips|) log n) if paths are long.
//
// Step 2 — tree DP after collapsing weights
// Define weighted cost w[u] = price[u] * freq[u]. Halving u saves w[u] / 2 on payments through u
// (cost becomes w[u]/2). Adjacent halving forbidden ⇒ chosen halving vertices form an independent
// set — weighted MIS-style DP on a tree.
// State: dfs(u, prev, parentHalved) = minimum total downstream contribution for the subtree rooted at
// u when edge (parent(u), u) is fixed and parentHalved tells whether parent’s price was halved.
// Transitions at u:
//   - Always allowed: pay full w[u] at u; children see parentHalved = False.
//   - If parent was NOT halved, optionally halve u: pay w[u]//2 at u; children must see
//     parentHalved = True (cannot halve a child if u is halved — equivalent constraint).
//   - If parent WAS halved, u cannot be halved — only full-price branch.
// Answer: dfs(root, -1, False). Root 0 after fixing an arbitrary tree orientation.
//
// Why this DP is correct
// On a tree, decisions at children depend only on whether their parent took half pricing — global
// independence constraint propagates exactly this one bit; subtrees are independent given that bit.
//
// Time complexity
// - Path marking: O(total nodes across all trip paths) <= O(n * |trips|) worst case.
// - DP: O(n) states with degree-sum work -> O(n).
//
// Space complexity
// - O(n) for graph, freq, recursion stack / memo (e.g. lru_cache depth O(n) worst).
//
// Edge cases
// - freq[u] == 0: node never used by trips — contributes 0 regardless of halving (still consistent).
// - Single node trips (start == end): path is one node; freq increments correctly via DFS base case.
// - price halving uses integer division // per statement / examples.
//
// Improvements
// - Binary lifting LCA + difference array for frequencies when paths are long and many trips.
// - Iterative DP / explicit memo table instead of lru_cache if recursion depth is a concern (convert
//   tree to rooted order via stack).
//
// LeetCode submission
// Put `from typing import List` and `functools.lru_cache` inside # @lc code=start.
//
// Interview walkthrough
// 1) Separate “how often each node is paid” from “which nodes we halve”.
// 2) Recognize independent-set structure on a tree -> parent-state DP.
// 3) Implement freq then DP; discuss faster freq counting if asked.
// --- end notes ---
//
// @lc code=start

// MinimumTotalPrice2646 returns the minimum total cost across all trips after halving
// a set of non-adjacent nodes.
func MinimumTotalPrice2646(n int, edges [][]int, price []int, trips [][]int) int64 {
	g := make([][]int, n)
	for _, e := range edges {
		u, v := e[0], e[1]
		g[u] = append(g[u], v)
		g[v] = append(g[v], u)
	}

	freq := make([]int64, n)

	markPath := func(start, end int) {
		parent := make([]int, n)
		for i := 0; i < n; i++ {
			parent[i] = -1
		}
		stack := make([]int, 0, n)
		stack = append(stack, start)
		parent[start] = start

		for len(stack) > 0 {
			u := stack[len(stack)-1]
			stack = stack[:len(stack)-1]
			if u == end {
				break
			}
			for _, v := range g[u] {
				if parent[v] != -1 {
					continue
				}
				parent[v] = u
				stack = append(stack, v)
			}
		}

		// backtrack end -> start
		cur := end
		for {
			freq[cur]++
			if cur == start {
				break
			}
			cur = parent[cur]
		}
	}

	for _, t := range trips {
		markPath(t[0], t[1])
	}

	// Root tree at 0, build parent order.
	par := make([]int, n)
	order := make([]int, 0, n)
	for i := 0; i < n; i++ {
		par[i] = -1
	}
	st := []int{0}
	par[0] = 0
	for len(st) > 0 {
		u := st[len(st)-1]
		st = st[:len(st)-1]
		order = append(order, u)
		for _, v := range g[u] {
			if par[v] != -1 {
				continue
			}
			par[v] = u
			st = append(st, v)
		}
	}

	dp0 := make([]int64, n) // u not halved
	dp1 := make([]int64, n) // u halved

	for i := n - 1; i >= 0; i-- {
		u := order[i]
		wFull := int64(price[u]) * freq[u]
		wHalf := int64(price[u]/2) * freq[u]

		var sum0 int64 = wFull
		var sum1 int64 = wHalf
		for _, v := range g[u] {
			if v == par[u] {
				continue
			}
			// if u not halved, child can be halved or not
			if dp0[v] < dp1[v] {
				sum0 += dp0[v]
			} else {
				sum0 += dp1[v]
			}
			// if u halved, child cannot be halved
			sum1 += dp0[v]
		}
		dp0[u] = sum0
		dp1[u] = sum1
	}

	if dp0[0] < dp1[0] {
		return dp0[0]
	}
	return dp1[0]
}

// @lc code=end

