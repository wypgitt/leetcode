//
// @lc app=leetcode id=272 lang=python3
//
// [272] Closest Binary Search Tree Value II
//

// =============================================================================
// PROBLEM (precise)
// =============================================================================
//
// Given the root of a binary search tree, a **target** (often float), and integer
// **k**, return **exactly k** node values whose numeric distance to **target** is
// smallest among all nodes. If multiple nodes tie for distance, usually prefer the
// **smaller** value first (LeetCode convention — reflected in tie-breaking below).
//
// =============================================================================
// WHY THIS APPROACH (algorithm choice)
// =============================================================================
//
// **BST invariant:** an **inorder traversal** visits keys in **strictly sorted**
// order (assuming distinct BST keys as is typical on LC).
//
// Once values are sorted in array **vals**, finding **k** closest to **target** is a
// **two-pointer expansion** around the interval where **target** would be inserted:
// - Locate split index **i = bisect_left(vals, target)** so values `< target` are to
//   the left and values `>= target` to the right (adjust semantics if duplicates).
// - Initialize **left = i - 1**, **right = i**, then repeatedly pick the side whose
//   endpoint is **strictly closer** to **target**; on **equal** distance, pick the
//   **smaller** number (move **left** first) — matches typical tie rule.
//
// **Alternatives (trade-offs to mention in interviews):**
//
// - **Max-heap of size k** storing (-distance, value) while traversing: **O(n log k)**
//   time, **O(k)** space — never stores full sorted list; good if **k ≪ n** and tree
//   is huge (still must visit every node unless combined with pruning — BST alone
//   doesn’t reduce worst-case visit without extra structure).
//
// - **Two-stack predecessor/successor iterators:** simulate **prev** and **next** on a
//   BST without materializing all nodes — **O(h + k)** extra space, **O(n)** time in
//   worst case to advance pointers enough — elegant but longer to code under time
//   pressure.
//
// Here we choose **inorder + two pointers**: **simple**, easy to prove correct, **O(n)**
// time / **O(n)** auxiliary for the sorted snapshot — standard “hire loop” solution.
//
// =============================================================================
// DATA STRUCTURES
// =============================================================================
//
// - **vals:** Python **list** holding inorder sequence — **O(n)** space.
// - **Iterative inorder stack:** explicit **list as stack** for traversal — avoids deep
//   recursion on skewed trees; still **O(h)** stack frames worst-case height **h**.
// - **bisect_left** from **bisect** module on sorted **vals** — **O(log n)** locate split.
//
// No hash map needed — ordering comes from BST structure.
//
// =============================================================================
// TIME & SPACE COMPLEXITY (analysis)
// =============================================================================
//
// **Time:**
// - Inorder visits each node once → **O(n)**.
// - Bisect on length **n** → **O(log n)**.
// - Each pointer moves at most **n** steps total while collecting **k** answers → **O(k)**.
// - Overall **O(n)** dominated by traversal.
//
// **Space:**
// - **vals** stores **n** integers → **O(n)** auxiliary (plus **O(h)** stack during inorder,
//   absorbed into **O(n)** worst case on skewed tree where **h = n**).
//
// **Improvement axis:** reduce extra space using iterator-based successor/predecessor
// (**O(h)** memory) at the cost of implementation complexity.
//
// =============================================================================
// EDGE CASES
// =============================================================================
//
// - **Empty tree:** return **[]**.
// - **k ≥ n:** collect entire inorder list; merge still completes in **k** steps when
//   **k == n** (both pointers exhaust predictably).
// - **k == 1:** degenerates to closest single value — same code path.
// - **Target smaller than min / larger than max:** one-sided expansion only.
// - **Duplicate values in BST:** LC sometimes forbids dupes in BST definition; if dupes
//   exist, ordering/tie rules may need clarification — standard BST assumption here.
//
// =============================================================================
// TESTING
// =============================================================================
//
// - Small handcrafted trees + brute force (collect all values, sort by distance then
//   value tie-break, take **k**).
// - Random BST shapes via insertion order vs brute.
//
// =============================================================================
//
// @lc code=start

package leetcode

//
// @lc app=leetcode id=272 lang=golang
//
// [272] Closest Binary Search Tree Value II
//
// =============================================================================
// PROBLEM (precise)
// =============================================================================
//
// Given the root of a binary search tree, a **target** (often float), and integer
// **k**, return **exactly k** node values whose numeric distance to **target** is
// smallest among all nodes. If multiple nodes tie for distance, usually prefer the
// **smaller** value first (LeetCode convention — reflected in tie-breaking below).
//
// =============================================================================
// WHY THIS APPROACH (algorithm choice)
// =============================================================================
//
// **BST invariant:** an **inorder traversal** visits keys in **strictly sorted**
// order (assuming distinct BST keys as is typical on LC).
//
// Once values are sorted in array **vals**, finding **k** closest to **target** is a
// **two-pointer expansion** around the interval where **target** would be inserted:
// - Locate split index **i = bisect_left(vals, target)** so values `< target` are to
//   the left and values `>= target` to the right (adjust semantics if duplicates).
// - Initialize **left = i - 1**, **right = i**, then repeatedly pick the side whose
//   endpoint is **strictly closer** to **target**; on **equal** distance, pick the
//   **smaller** number (move **left** first) — matches typical tie rule.
//
// **Alternatives (trade-offs to mention in interviews):**
//
// - **Max-heap of size k** storing (-distance, value) while traversing: **O(n log k)**
//   time, **O(k)** space — never stores full sorted list; good if **k ≪ n** and tree
//   is huge (still must visit every node unless combined with pruning — BST alone
//   doesn’t reduce worst-case visit without extra structure).
//
// - **Two-stack predecessor/successor iterators:** simulate **prev** and **next** on a
//   BST without materializing all nodes — **O(h + k)** extra space, **O(n)** time in
//   worst case to advance pointers enough — elegant but longer to code under time
//   pressure.
//
// Here we choose **inorder + two pointers**: **simple**, easy to prove correct, **O(n)**
// time / **O(n)** auxiliary for the sorted snapshot — standard “hire loop” solution.
//
// =============================================================================
// DATA STRUCTURES
// =============================================================================
//
// - **vals:** slice holding inorder sequence — **O(n)** space.
// - **Iterative inorder stack:** explicit slice as stack — avoids deep recursion on
//   skewed trees; still **O(h)** stack frames worst-case height **h**.
// - Binary search on sorted **vals** — **O(log n)** locate split.
//
// =============================================================================
// TIME & SPACE COMPLEXITY (analysis)
// =============================================================================
//
// **Time:**
// - Inorder visits each node once → **O(n)**.
// - Bisect on length **n** → **O(log n)**.
// - Each pointer moves at most **n** steps total while collecting **k** answers → **O(k)**.
// - Overall **O(n)** dominated by traversal.
//
// **Space:**
// - **vals** stores **n** integers → **O(n)** auxiliary (plus **O(h)** stack during inorder,
//   absorbed into **O(n)** worst case on skewed tree where **h = n**).
//
// =============================================================================
// EDGE CASES
// =============================================================================
//
// - **Empty tree:** return **[]**.
// - **k ≥ n:** collect entire inorder list; merge still completes in **k** steps when
//   **k == n** (both pointers exhaust predictably).
// - **k == 1:** degenerates to closest single value — same code path.
// - **Target smaller than min / larger than max:** one-sided expansion only.
//
// =============================================================================
//
// @lc code=start

import "sort"

// ClosestKValues272 returns k values in BST closest to target.
func ClosestKValues272(root *TreeNode, target float64, k int) []int {
	if root == nil || k <= 0 {
		return nil
	}

	vals := make([]int, 0)
	stack := make([]*TreeNode, 0)
	cur := root
	for cur != nil || len(stack) > 0 {
		for cur != nil {
			stack = append(stack, cur)
			cur = cur.Left
		}
		cur = stack[len(stack)-1]
		stack = stack[:len(stack)-1]
		vals = append(vals, cur.Val)
		cur = cur.Right
	}

	n := len(vals)
	if k > n {
		k = n
	}

	i := sort.Search(len(vals), func(idx int) bool { return float64(vals[idx]) >= target })
	left, right := i-1, i
	out := make([]int, 0, k)

	for len(out) < k {
		if left < 0 {
			out = append(out, vals[right])
			right++
			continue
		}
		if right >= n {
			out = append(out, vals[left])
			left--
			continue
		}
		ld := target - float64(vals[left])
		if ld < 0 {
			ld = -ld
		}
		rd := target - float64(vals[right])
		if rd < 0 {
			rd = -rd
		}
		if ld <= rd {
			out = append(out, vals[left])
			left--
		} else {
			out = append(out, vals[right])
			right++
		}
	}

	return out
}

// @lc code=end

