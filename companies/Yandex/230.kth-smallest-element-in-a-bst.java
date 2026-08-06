import java.util.*;

/**
 * Algorithm:
 * Iterative inorder traversal of a BST visits values in ascending order. The
 * kth popped node is the answer.
 *
 * Java data structures:
 * ArrayDeque<TreeNode> is the explicit traversal stack.
 *
 * Complexity:
 * Time O(h + k), space O(h).
 */
class Solution {
    public int kthSmallest(TreeNode root, int k) {
        Deque<TreeNode> stack = new ArrayDeque<>();
        TreeNode node = root;
        while (true) {
            while (node != null) {
                stack.push(node);
                node = node.left;
            }
            node = stack.pop();
            if (--k == 0) {
                return node.val;
            }
            node = node.right;
        }
    }
}

