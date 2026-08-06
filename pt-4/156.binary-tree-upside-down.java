/**
 * Algorithm:
 * Iteratively rotate the tree along the left spine. The old parent becomes the
 * new right child, and the old parent's right child becomes the new left child.
 *
 * Complexity:
 * Time O(h) for the left spine length, space O(1).
 */
class Solution {
    public TreeNode upsideDownBinaryTree(TreeNode root) {
        TreeNode parent = null;
        TreeNode parentRight = null;
        TreeNode cur = root;
        while (cur != null) {
            TreeNode nextLeft = cur.left;
            cur.left = parentRight;
            parentRight = cur.right;
            cur.right = parent;
            parent = cur;
            cur = nextLeft;
        }
        return parent;
    }
}

