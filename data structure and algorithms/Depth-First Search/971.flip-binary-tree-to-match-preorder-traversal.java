/*
 * @lc app=leetcode id=971 lang=java
 *
 * [971] Flip Binary Tree To Match Preorder Traversal
 */

/*
 * --- Interview notes (preorder simulation, greedy choice at each node, DFS, complexity) ---
 *
 * Problem
 * You are given the **`root`** of a binary tree and an array **`voyage`** — the **target preorder traversal** (values in the
 * order a preorder walk should visit nodes). You may **flip** any node any number of times: a **flip** swaps **`left`** and
 * **`right`** children (subtrees). Return the list of **values of nodes where you performed a flip**, in the order you flip.
 * If no sequence of flips can make the tree’s preorder equal **`voyage`**, return **`[-1]`**.
 *
 * Key observation — preorder structure
 * Preorder is **`root → preorder(left) → preorder(right)`**. After visiting **`root`**, the **next** value in preorder is:
 * • **Left child exists** (and we treat “promoted” side first): the **root value of the next subtree visited**.
 * • If **both** children exist **without** a flip at **`root`**, that next value **must** be **`left.val`** (start of left subtree’s
 *   preorder).
 * • If **both** children exist **with** a flip at **`root`**, children swap; preorder becomes **`root → preorder(right) →
 *   preorder(left)`**, so the next value **must** be **`right.val`**.
 *
 * Greedy choice (why it is correct)
 * At each node with **two** children, the **first** value after **`root`** in **`voyage`** uniquely tells us whether we need a
 * flip: match **`voyage[i]`** to **`left.val`** vs **`right.val`**. There is **no** lookahead trade-off — flipping later cannot
 * fix a wrong choice here because preorder **fixes** which subtree comes first **immediately** after **`root`**. So **one DFS**
 * that consumes **`voyage`** in lockstep is optimal and runs in **linear** time.
 *
 * Algorithm — DFS with index pointer
 * Maintain **`i`**, the index of the **next** expected preorder value.
 * **`dfs(node)`**:
 * 1. **Empty node** — return **`True`** (nothing to match).
 * 2. **`voyage[i] != node.val`** or **`i` out of range** — **fail**.
 * 3. **`i += 1`** (consume **`root`**).
 * 4. **Leaf** — **`True`**.
 * 5. **Only left child** — recurse **`left`** (next must start left subtree).
 * 6. **Only right child** — recurse **`right`**.
 * 7. **Both children** — if **`voyage[i] == left.val`**: recurse **`left`** then **`right`**. Else if **`voyage[i] ==
 *    right.val`**: **record `node.val`** in **`flips`**, recurse **`right`** then **`left`**. Else **fail**.
 * After DFS, success iff **`dfs(root)`** and **`i == len(voyage)`** (tree and array fully consumed together).
 *
 * Data structures
 * • **`voyage`** — input array (**O(n)`**).
 * • **`flips`** — list of flipped node values (**O(f) ⊆ O(n)`**).
 * • **Integer `i`** — cursor; **O(1)** extra space.
 * • **Recursion stack** — **O(h)`** height **`h`** (balanced **`O(log n)`**, skewed **`O(n)`**).
 *
 * Time complexity **O(n)`** — each node visited once; each **`voyage`** index advanced at most once per node visit.
 *
 * Space complexity **O(h)`** auxiliary for recursion (**output `flips` not counted** as extra problem space); **O(n)`** if output
 * lists all flips in worst case.
 *
 * Edge cases
 * • **`voyage`** length **≠** number of nodes — impossible (**`[-1]`**).
 * • **Single node** — **`voyage == [root.val]`**, **`[]`** flips.
 * • **Chain (one child each level)** — no flip decisions at two-child nodes; only value checks.
 * • **Both children, next value matches neither** — **`[-1]`** immediately at that node.
 *
 * Tests (mental / quick)
 * • Example shape: root **1**, children **2** and **3**; **`voyage = [1,3,2]`** → must flip at **1**, **`flips = [1]`**.
 * • **`voyage`** order **`[1,2,3]`** → no flip, **`flips = []`**.
 *
 * Improvements
 * • **Iterative DFS** with explicit stack + same logic removes recursion overhead (same asymptotics).
 * • **Early exit**: on first failure return **`[-1]`** without completing traversal (already implemented via boolean).
 *
 * --- end notes ---
 */

import java.util.ArrayList;
import java.util.Collections;
import java.util.List;

/**
 * Definition for a binary tree node (provided by LeetCode).
 */
class TreeNode {
    int val;
    TreeNode left;
    TreeNode right;

    TreeNode() {}

    TreeNode(int val) {
        this.val = val;
    }

    TreeNode(int val, TreeNode left, TreeNode right) {
        this.val = val;
        this.left = left;
        this.right = right;
    }
}

// @lc code=start
class Solution {
    private int i;
    private List<Integer> flips;
    private int[] voyage;

    public List<Integer> flipMatchVoyage(TreeNode root, int[] voyage) {
        this.voyage = voyage;
        i = 0;
        flips = new ArrayList<>();
        if (dfs(root) && i == voyage.length) {
            return flips;
        }
        return Collections.singletonList(-1);
    }

    private boolean dfs(TreeNode node) {
        if (node == null) {
            return true;
        }
        if (i >= voyage.length || node.val != voyage[i]) {
            return false;
        }
        i++;

        if (node.left == null && node.right == null) {
            return true;
        }
        if (node.left != null && node.right == null) {
            return dfs(node.left);
        }
        if (node.right != null && node.left == null) {
            return dfs(node.right);
        }

        if (i >= voyage.length) {
            return false;
        }
        if (voyage[i] == node.left.val) {
            return dfs(node.left) && dfs(node.right);
        }
        if (voyage[i] == node.right.val) {
            flips.add(node.val);
            return dfs(node.right) && dfs(node.left);
        }
        return false;
    }
}
// @lc code=end
