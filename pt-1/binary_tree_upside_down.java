/*
 * LeetCode 156. Binary Tree Upside Down
 * https://leetcode.com/problems/binary-tree-upside-down/
 *
 * Mirrors binary_tree_upside_down.py: iterative walk on left spine; recursive variant below.
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

/**
 * Same algorithm recursively (O(h) stack). Package-private so this file keeps a single public
 * top-level class for the judge.
 */
class SolutionRecursive {
    public TreeNode upsideDownBinaryTree(TreeNode root) {
        if (root == null || root.left == null) {
            return root;
        }
        TreeNode newRoot = upsideDownBinaryTree(root.left);
        root.left.left = root.right;
        root.left.right = root;
        root.left = null;
        root.right = null;
        return newRoot;
    }
}
// @lc code=end
