//
// @lc app=leetcode id=1019 lang=python3
//
// [1019] Next Greater Node In Linked List
//
//
// --- Interview notes (next greater element, monotone stack, amortized analysis, complexity, edges) ---
//
// Problem
// For each node in a singly linked list (left-to-right order), output the **value** of the **nearest node strictly to the
// right** whose value is **strictly larger**; if none exists, output **`0`**. Return results as an integer array aligned with
// node order.
//
// Reduction to “next greater element” (NGE)
// Ignore linked-list pointer mechanics for a moment: indices **`0 … n−1`** carry values **`v[i]`**. We need **`ans[i]`** =
// **`v[j]`** for smallest **`j > i`** with **`v[j] > v[i]`**, else **`0`**. This is the classic **next greater element to the
// right** pattern.
//
// Why a monotone decreasing stack (indices)
// Scan **`i = 0 … n−1`**. Maintain a stack of indices whose values form a **strictly decreasing** sequence from bottom to
// top (next candidates awaiting a “greater to the right”).
// When **`v[i]`** arrives, it resolves **all** pending indices whose value is **smaller** than **`v[i]`**: repeatedly pop
// **`idx`** from the stack and set **`ans[idx] = v[i]`** — **`i`** is the **first** position to the right beating those
// values because smaller intervening values were already discarded when their own greater appeared or never will block **`i`**.
// Push **`i`** afterward.
// Each index is **pushed once** and **popped at most once** ⇒ **O(n)** total stack work.
//
// Linked list handling
// First walk **`head → …`** and collect **`vals`** in order (**O(n)** time, **O(n)** space). This separation keeps the stack
// logic identical to the array version (clean interview explanation).
//
// Data structures
// • **`vals: List[int]`** — random access for comparisons.
// • **`stack: List[int]`** — index stack (**Python list as stack**).
// • **`ans`** initialized to **`0`** — default “no greater element”.
//
// Time complexity **O(n)** — single list traversal + single index sweep with amortized **O(1)** stack ops per position.
//
// Space complexity **O(n)** — **`vals`**, **`ans`**, and stack together **O(n)**.
//
// Edge cases
// • **Strictly increasing** list — every position gets **0** (except none actually; last always 0). Actually strictly
//   increasing: each node sees next larger except last gets 0. Wait: **increasing** values mean each element has next
//   greater except last — **ans[i] = v[i+1]** for non-last.
// • **Non-increasing** — first element may see first smaller… actually decreasing: first gets 0 until larger appears...
// • **Single node** — **`[0]`**.
// • **Empty list** — **`[]`** (guard **`head is None`**).
//
// Tests (statement-style)
// • **`[2,1,5]`** → **`[5,5,0]`**.
// • **`[2,7,4,3,5]`** → **`[7,0,5,5,0]`**.
//
// Improvements
// • **Space-sensitive**: stream nodes while storing node references in the stack and comparing **`node.val`** — still **O(n)**
//   stack worst-case but avoids **`vals`** duplicate array (same asymptotics overall).
//
// --- end notes ---
//
// @lc code=start

package leetcode

// Definition for singly-linked list.
// class ListNode:
//     def __init__(self, val=0, next=None):
//         self.val = val
//         self.next = next
func NextLargerNodes1019(head *ListNode) []int {
	vals := make([]int, 0, 128)
	for cur := head; cur != nil; cur = cur.Next {
		vals = append(vals, cur.Val)
	}
	n := len(vals)
	ans := make([]int, n)
	stk := make([]int, 0, n)
	for i := 0; i < n; i++ {
		for len(stk) > 0 && vals[stk[len(stk)-1]] < vals[i] {
			idx := stk[len(stk)-1]
			stk = stk[:len(stk)-1]
			ans[idx] = vals[i]
		}
		stk = append(stk, i)
	}
	return ans
}

// @lc code=end

