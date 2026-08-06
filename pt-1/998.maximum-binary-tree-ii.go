package leetcode

//
// @lc app=leetcode id=998 lang=golang
//
// [998] Maximum Binary Tree Ii
//

// --- Interview notes (max-tree definition, append semantics, recursion on right spine, complexity, iteration variant) ---
//
// Background — Maximum binary tree from an array
// From array `a`, pick index `i` of the **maximum** element; root value is `a[i]`; left child is `Construct(a[0:i])`,
// right child is `Construct(a[i+1:])`. Every node’s value is larger than **all** values in its subtrees (max-heap property
// on values along root-to-leaf max paths — “maximum tree”).
//
// What we are given / asked
// The tree `root` equals `Construct(a)` for some unknown array `a` of **distinct** integers. Form `b = a` with `val`
// **appended at the end** (`b = a + [val]`). Return `Construct(b)` **without** reconstructing `a`.
//
// Why the new value only affects the **right spine**
// In `b`, everything before `val` still appears in order as a prefix; `val` is the **last** element. In the construction,
// the global maximum of `b` is either:
// • **Still** the same element as in `a` (if `val` is not the new maximum) — then that node stays the root, and `val` lies
//   entirely in the **suffix after** the old maximum’s position in `b`, i.e. strictly to the **right** of the old root in
//   the in-order / array sense — which corresponds to the **right subtree** of the root. Recurse on `root.right`.
// • **Or** `val` is larger than every element of `a` — then `val` is the unique maximum of `b`, so it becomes the **new
//   root**, and the entire old tree is exactly the elements **to the left** of the maximum in `b`, hence the **left**
//   child: `TreeNode(val, left=root, right=None)`.
//
// Algorithm (recursive)
// • If `root` is `None` or `root.val < val`: new root is `TreeNode(val, root, None)` — old tree hangs on the left.
// • Else: `root.right = insertIntoMaxTree(root.right, val)` and return `root`.
//
// Correctness at each recursive step mirrors “insert at end of conceptual array” inside the current right chain until we
// either become new maximum (attach as new node whose left is previous subtree) or attach as leaf/further right.
//
// Data structures
// Only pointer rewiring on the existing binary tree — **no auxiliary arrays or hash maps**.
//
// Time complexity **O(h)** with `h` height of tree — worst **O(n)** for skewed tree; typical **O(log n)** if balanced-ish.
// Space **O(h)** recursion stack (iterative version below uses **O(1)** extra).
//
// Edge cases
// • `val` larger than every existing node — new root, old root left child (matches Example 1).
// • `val` smallest — walk to rightmost path and append (Examples 2–3 style behavior along right spine).
//
// Tests (statement)
// • Example 1: `root = [4,1,3,null,null,2]`, `val = 5` → `[5,4,null,1,3,null,null,2]` (`a = [1,4,2,3]`, `b` adds `5`).
// • Examples 2–3: smaller `val` attaches along right chain (see problem drawings).
//
// Improvement — iterative
// While `curr.right` exists and `curr.right.val > val`, move `curr = curr.right`. Then insert node `val` with
// `node.left = curr.right`, `curr.right = node` (or if `root.val < val`, return `TreeNode(val, root)`). **O(1)** extra
// space.
//
// --- end notes ---

// @lc code=start

// InsertIntoMaxTree998 inserts val into an existing maximum binary tree that
// corresponds to appending val to the original array.
func InsertIntoMaxTree998(root *TreeNode, val int) *TreeNode {
	if root == nil || root.Val < val {
		return &TreeNode{Val: val, Left: root}
	}
	root.Right = InsertIntoMaxTree998(root.Right, val)
	return root
}

// @lc code=end

