package leetcode

import "math"

//
// @lc app=leetcode id=1008 lang=golang
//
// [1008] Construct Binary Search Tree From Preorder Traversal
//

// --- Interview notes (BST preorder shape, upper-bound DFS, why O(n), stack variant, complexity, edges) ---
//
// Problem
// Given **distinct** integers in **preorder** order of some BST, reconstruct that BST (answer unique).
//
// Preorder structure
// Order is **root**, then preorder of **left** subtree, then preorder of **right** subtree. All values in the left subtree
// are **< root.val**; all in the right subtree are **> root.val** (BST property).
//
// Key observation — single upper bound suffices
// Scan preorder left-to-right while maintaining an **upper bound** `hi` on values allowed in the current subtree:
// • Read the next value `v` if `v <= hi` (strict BST: values `< parent` on left chain — implementation uses `v > hi` as stop).
// • That value becomes the local root. Its **left** subtree contains only values `< v`, so recurse with bound **`v`**.
// • Its **right** subtree contains values in `(v, hi)` (still under the same ancestor cap `hi`), so recurse right with the
// **same** `hi` passed into this call.
// When the next preorder value exceeds `hi`, it belongs to an **ancestor’s right** subtree — return `None` without
// consuming (caller’s sibling/right branch will take it).
//
// Algorithm (`dfs(hi)`)
// • If index at end **or** `preorder[i] > hi`, return `None`.
// • Else take `preorder[i]` as root, advance `i`, build `left = dfs(root.val)`, `right = dfs(hi)` (same `hi` as parent scope).
// • Start with `dfs(+∞)`.
//
// Why not rebuild min/max every time
// Equivalent to **(lo, hi)** interval DFS; carrying only `hi` works because left recursion naturally tightens the cap via
// `root.val` en route.
//
// Time complexity **O(n)** — each element pushed as a node exactly once; each index advanced once.
//
// Space complexity **O(h)** recursion stack — **O(n)** worst (skewed tree), **O(log n)** balanced.
//
// Data structures
// Only tree pointers; **no auxiliary stack/array** beyond recursion (except index integer).
//
// Edge cases
// • **One node** — root only, no recursive stops triggered incorrectly.
// • **Increasing preorder** (linked chain right spine) — recursion depth **O(n)**.
//
// Alternative — explicit stack simulation
// Push nodes while values decrease; on increase, pop until parent found — **O(n)** time, **O(n)** explicit stack; same idea as
// Morris-like boundary walking.
//
// Tests (sanity)
// • `[8,5,1,7,10,12]` builds BST with root `8`, left `5`, etc.
// • `[4,2]` → root `4`, left `2`.
//
// Improvements
// • Iterative stack version avoids deep recursion limits on skewed trees (language-dependent).
//
// --- end notes ---

// @lc code=start

// BstFromPreorder1008 reconstructs a BST from its preorder traversal.
func BstFromPreorder1008(preorder []int) *TreeNode {
	i := 0

	var dfs func(hi int) *TreeNode
	dfs = func(hi int) *TreeNode {
		if i == len(preorder) || preorder[i] > hi {
			return nil
		}
		v := preorder[i]
		i++
		root := &TreeNode{Val: v}
		root.Left = dfs(v)
		root.Right = dfs(hi)
		return root
	}

	return dfs(math.MaxInt)
}

// @lc code=end

