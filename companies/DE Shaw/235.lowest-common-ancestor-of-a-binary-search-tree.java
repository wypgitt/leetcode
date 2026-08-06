/**
 * Algorithm:
 * In a BST, if both target values are less than the current node, the LCA is in
 * the left subtree; if both are greater, it is in the right subtree. Otherwise
 * the current node splits the targets and is the LCA.
 *
 * Complexity:
 * Time O(h), space O(1).
 */
class Solution {
    public TreeNode lowestCommonAncestor(TreeNode root, TreeNode p, TreeNode q) {
        int low = Math.min(p.val, q.val);
        int high = Math.max(p.val, q.val);
        TreeNode node = root;
        while (node != null) {
            if (high < node.val) {
                node = node.left;
            } else if (low > node.val) {
                node = node.right;
            } else {
                return node;
            }
        }
        return null;
    }
}

