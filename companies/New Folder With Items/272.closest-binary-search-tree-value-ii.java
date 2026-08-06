/*
 * @lc app=leetcode id=272 lang=java
 *
 * [272] Closest Binary Search Tree Value II
 */

/*
 * =============================================================================
 * PROBLEM (precise)
 * =============================================================================
 *
 * Given the root of a binary search tree, a **target** (often float), and integer
 * **k**, return **exactly k** node values whose numeric distance to **target** is
 * smallest among all nodes. If multiple nodes tie for distance, usually prefer the
 * **smaller** value first (LeetCode convention — reflected in tie-breaking below).
 *
 * =============================================================================
 * WHY THIS APPROACH (algorithm choice)
 * =============================================================================
 *
 * **BST invariant:** an **inorder traversal** visits keys in **strictly sorted**
 * order (assuming distinct BST keys as is typical on LC).
 *
 * Once values are sorted in array **vals**, finding **k** closest to **target** is a
 * **two-pointer expansion** around the interval where **target** would be inserted:
 * - Locate split index **i = bisect_left(vals, target)** so values `< target` are to
 *   the left and values `>= target` to the right (adjust semantics if duplicates).
 * - Initialize **left = i - 1**, **right = i**, then repeatedly pick the side whose
 *   endpoint is **strictly closer** to **target**; on **equal** distance, pick the
 *   **smaller** number (move **left** first) — matches typical tie rule.
 *
 * **Alternatives (trade-offs to mention in interviews):**
 *
 * - **Max-heap of size k** storing (-distance, value) while traversing: **O(n log k)**
 *   time, **O(k)** space — never stores full sorted list; good if **k ≪ n** and tree
 *   is huge (still must visit every node unless combined with pruning — BST alone
 *   doesn’t reduce worst-case visit without extra structure).
 *
 * - **Two-stack predecessor/successor iterators:** simulate **prev** and **next** on a
 *   BST without materializing all nodes — **O(h + k)** extra space, **O(n)** time in
 *   worst case to advance pointers enough — elegant but longer to code under time
 *   pressure.
 *
 * Here we choose **inorder + two pointers**: **simple**, easy to prove correct, **O(n)**
 * time / **O(n)** auxiliary for the sorted snapshot — standard “hire loop” solution.
 *
 * =============================================================================
 * DATA STRUCTURES
 * =============================================================================
 *
 * - **vals:** **ArrayList** holding inorder sequence — **O(n)** space.
 * - **Iterative inorder stack:** explicit **Deque** for traversal — avoids deep
 *   recursion on skewed trees; still **O(h)** stack worst-case height **h**.
 * - **bisect_left** on sorted **vals** — **O(log n)** locate split.
 *
 * No hash map needed — ordering comes from BST structure.
 *
 * =============================================================================
 * TIME & SPACE COMPLEXITY (analysis)
 * =============================================================================
 *
 * **Time:**
 * - Inorder visits each node once → **O(n)**.
 * - Bisect on length **n** → **O(log n)**.
 * - Each pointer moves at most **n** steps total while collecting **k** answers → **O(k)**.
 * - Overall **O(n)** dominated by traversal.
 *
 * **Space:**
 * - **vals** stores **n** integers → **O(n)** auxiliary (plus **O(h)** stack during inorder,
 *   absorbed into **O(n)** worst case on skewed tree where **h = n**).
 *
 * **Improvement axis:** reduce extra space using iterator-based successor/predecessor
 * (**O(h)** memory) at the cost of implementation complexity.
 *
 * =============================================================================
 * EDGE CASES
 * =============================================================================
 *
 * - **Empty tree:** return **[]**.
 * - **k ≥ n:** collect entire inorder list; merge still completes in **k** steps when
 *   **k == n** (both pointers exhaust predictably).
 * - **k == 1:** degenerates to closest single value — same code path.
 * - **Target smaller than min / larger than max:** one-sided expansion only.
 * - **Duplicate values in BST:** LC sometimes forbids dupes in BST definition; if dupes
 *   exist, ordering/tie rules may need clarification — standard BST assumption here.
 *
 * =============================================================================
 * TESTING
 * =============================================================================
 *
 * - Small handcrafted trees + brute force (collect all values, sort by distance then
 *   value tie-break, take **k**).
 * - Random BST shapes via insertion order vs brute.
 *
 * =============================================================================
 */

// @lc code=start
import java.util.ArrayDeque;
import java.util.ArrayList;
import java.util.Deque;
import java.util.List;

/**
 * Definition for a binary tree node.
 * public class TreeNode {
 *     int val;
 *     TreeNode left;
 *     TreeNode right;
 *     TreeNode() {}
 *     TreeNode(int val) { this.val = val; }
 *     TreeNode(int val, TreeNode left, TreeNode right) {
 *         this.val = val;
 *         this.left = left;
 *         this.right = right;
 *     }
 * }
 */
class Solution {
    /**
     * Inorder flatten BST to sorted values, locate split around target, expand two
     * pointers picking the closer endpoint each step (smaller on ties).
     */
    public List<Integer> closestKValues(TreeNode root, double target, int k) {
        List<Integer> res = new ArrayList<>();
        if (root == null || k <= 0) {
            return res;
        }

        List<Integer> vals = new ArrayList<>();
        Deque<TreeNode> stack = new ArrayDeque<>();
        TreeNode cur = root;
        while (!stack.isEmpty() || cur != null) {
            while (cur != null) {
                stack.push(cur);
                cur = cur.left;
            }
            cur = stack.pop();
            vals.add(cur.val);
            cur = cur.right;
        }

        int n = vals.size();
        int i = bisectLeft(vals, target);
        int left = i - 1;
        int right = i;
        int need = Math.min(k, n);
        while (res.size() < need) {
            if (left < 0) {
                res.add(vals.get(right));
                right++;
            } else if (right >= n) {
                res.add(vals.get(left));
                left--;
            } else if (Math.abs(vals.get(left) - target) <= Math.abs(vals.get(right) - target)) {
                res.add(vals.get(left));
                left--;
            } else {
                res.add(vals.get(right));
                right++;
            }
        }
        return res;
    }

    /** First index i with vals.get(i) >= target (bisect_left). */
    private static int bisectLeft(List<Integer> vals, double target) {
        int lo = 0;
        int hi = vals.size();
        while (lo < hi) {
            int mid = (lo + hi) >>> 1;
            if (vals.get(mid) < target) {
                lo = mid + 1;
            } else {
                hi = mid;
            }
        }
        return lo;
    }
}
// @lc code=end
