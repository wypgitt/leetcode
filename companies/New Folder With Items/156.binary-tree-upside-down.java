/*
 * @lc app=leetcode id=156 lang=java
 *
 * [156] Binary Tree Upside Down
 */

/*
 * Problem (one level):
 *   Given a node with left child L and right child R, "flip" this triangle so that
 *   L becomes the new root, R becomes L's new left child, and the old root becomes
 *   L's new right child.
 *
 * Why iteration along the left spine works:
 *   The guarantee (every right node has a left sibling and no children) means the
 *   tree is effectively a chain along the left edge with optional right "buds".
 *   Processing from the original root downward is the same as flipping level by
 *   level from top to bottom; each step only needs the previous parent and that
 *   parent's old right child to wire the new left/right pointers.
 *
 * Variables:
 *   curr          — node we are rewiring this iteration (walking left).
 *   parent        — the node that was above curr in the original tree; becomes
 *                   curr's new right child after the flip at this step.
 *   parentRight   — the old right child of `parent` (sibling of curr in the
 *                   original tree); becomes curr's new left child. For the first
 *                   node we process, there is no such sibling yet, so null.
 */

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
    public TreeNode upsideDownBinaryTree(TreeNode root) {
        TreeNode curr = root;
        TreeNode parent = null;
        TreeNode parentRight = null;

        while (curr != null) {
            TreeNode left = curr.left;
            TreeNode right = curr.right;

            curr.left = parentRight;
            curr.right = parent;

            parentRight = right;
            parent = curr;
            curr = left;
        }

        return parent;
    }
}
// @lc code=end
