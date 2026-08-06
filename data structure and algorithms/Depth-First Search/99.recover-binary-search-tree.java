/**
 * Algorithm:
 * Inorder traversal of a BST should be increasing. Two swapped nodes create
 * one or two inversions. The first bad node is prev in the first inversion; the
 * second bad node is current in the last inversion. Swap their values.
 *
 * Complexity:
 * Time O(n), recursion space O(h).
 */
class Solution {
    private TreeNode first;
    private TreeNode second;
    private TreeNode prev;

    public void recoverTree(TreeNode root) {
        first = null;
        second = null;
        prev = null;
        inorder(root);
        int tmp = first.val;
        first.val = second.val;
        second.val = tmp;
    }

    private void inorder(TreeNode node) {
        if (node == null) {
            return;
        }
        inorder(node.left);
        if (prev != null && prev.val > node.val) {
            if (first == null) {
                first = prev;
            }
            second = node;
        }
        prev = node;
        inorder(node.right);
    }
}

