/*
 * @lc app=leetcode id=1019 lang=java
 *
 * [1019] Next Greater Node In Linked List
 */

/*
 * --- Interview notes (next greater element, monotone stack, amortized analysis, complexity, edges) ---
 *
 * Problem
 * For each node in a singly linked list (left-to-right order), output the **value** of the **nearest node strictly to the
 * right** whose value is **strictly larger**; if none exists, output **`0`**. Return results as an integer array aligned with
 * node order.
 *
 * Reduction to “next greater element” (NGE)
 * Ignore linked-list pointer mechanics for a moment: indices **`0 … n−1`** carry values **`v[i]`**. We need **`ans[i]`** =
 * **`v[j]`** for smallest **`j > i`** with **`v[j] > v[i]`**, else **`0`**. This is the classic **next greater element to the
 * right** pattern.
 *
 * Why a monotone decreasing stack (indices)
 * Scan **`i = 0 … n−1`**. Maintain a stack of indices whose values form a **strictly decreasing** sequence from bottom to
 * top (next candidates awaiting a “greater to the right”).
 * When **`v[i]`** arrives, it resolves **all** pending indices whose value is **smaller** than **`v[i]`**: repeatedly pop
 * **`idx`** from the stack and set **`ans[idx] = v[i]`** — **`i`** is the **first** position to the right beating those
 * values because smaller intervening values were already discarded when their own greater appeared or never will block **`i`**.
 * Push **`i`** afterward.
 * Each index is **pushed once** and **popped at most once** ⇒ **O(n)** total stack work.
 *
 * Linked list handling
 * First walk **`head → …`** and collect **`vals`** in order (**O(n)** time, **O(n)** space). This separation keeps the stack
 * logic identical to the array version (clean interview explanation).
 *
 * Data structures
 * • **`vals`** — random access for comparisons (`ArrayList<Integer>` or `int[]`).
 * • **`Deque<Integer>`** — index stack (Java `ArrayDeque`).
 * • **`ans`** initialized to **`0`** — default “no greater element”.
 *
 * Time complexity **O(n)** — single list traversal + single index sweep with amortized **O(1)** stack ops per position.
 *
 * Space complexity **O(n)** — **`vals`**, **`ans`**, and stack together **O(n)**.
 *
 * Edge cases
 * • **Strictly increasing** list — each element has next greater except last gets 0.
 * • **Non-increasing** — resolved by stack pops when a larger value appears.
 * • **Single node** — **`[0]`**.
 * • **Empty list** — **`[]`** (guard **`head == null`**).
 *
 * Tests (statement-style)
 * • **`[2,1,5]`** → **`[5,5,0]`**.
 * • **`[2,7,4,3,5]`** → **`[7,0,5,5,0]`**.
 *
 * Improvements
 * • **Space-sensitive**: stream nodes while storing node references in the stack — still **O(n)** stack worst-case but avoids
 * **`vals`** duplicate array (same asymptotics overall).
 *
 * --- end notes ---
 */

import java.util.ArrayDeque;
import java.util.ArrayList;
import java.util.Deque;
import java.util.List;

/**
 * Definition for singly-linked list (provided by LeetCode).
 */
class ListNode {
    int val;
    ListNode next;

    ListNode() {}

    ListNode(int val) {
        this.val = val;
    }

    ListNode(int val, ListNode next) {
        this.val = val;
        this.next = next;
    }
}

// @lc code=start
class Solution {
    public int[] nextLargerNodes(ListNode head) {
        List<Integer> valsList = new ArrayList<>();
        while (head != null) {
            valsList.add(head.val);
            head = head.next;
        }
        int n = valsList.size();
        int[] vals = new int[n];
        for (int i = 0; i < n; i++) {
            vals[i] = valsList.get(i);
        }
        int[] ans = new int[n];
        Deque<Integer> stack = new ArrayDeque<>();
        for (int i = 0; i < n; i++) {
            while (!stack.isEmpty() && vals[stack.peekLast()] < vals[i]) {
                ans[stack.pollLast()] = vals[i];
            }
            stack.addLast(i);
        }
        return ans;
    }
}
// @lc code=end
