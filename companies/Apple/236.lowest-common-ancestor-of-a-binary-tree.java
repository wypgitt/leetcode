/**
 * Algorithm:
 * Recursive LCA in a general binary tree. If the current root is null, p, or q,
 * return it. If p and q are found in different subtrees, current root is the
 * LCA; otherwise return the non-null side.
 *
 * Complexity:
 * Time O(n), recursion space O(h).
 */
class Solution {
    public TreeNode lowestCommonAncestor(TreeNode root, TreeNode p, TreeNode q) {
        if (root == null || root == p || root == q) {
            return root;
        }
        TreeNode left = lowestCommonAncestor(root.left, p, q);
        TreeNode right = lowestCommonAncestor(root.right, p, q);
        if (left != null && right != null) {
            return root;
        }
        return left != null ? left : right;
    }
}

