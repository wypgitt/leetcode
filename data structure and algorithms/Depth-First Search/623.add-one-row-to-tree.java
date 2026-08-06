import java.util.*;

/**
 * Algorithm:
 * If depth is 1, create a new root. Otherwise BFS to nodes at depth - 1, then
 * insert new nodes between each such node and its old children.
 *
 * Java data structures:
 * ArrayDeque<TreeNode> is the BFS queue.
 *
 * Complexity:
 * Time O(n), space O(width).
 */
class Solution {
    public TreeNode addOneRow(TreeNode root, int val, int depth) {
        if (depth == 1) {
            TreeNode newRoot = new TreeNode(val);
            newRoot.left = root;
            return newRoot;
        }

        Queue<TreeNode> q = new ArrayDeque<>();
        q.offer(root);
        int currentDepth = 1;
        while (!q.isEmpty() && currentDepth < depth - 1) {
            for (int size = q.size(); size > 0; size--) {
                TreeNode node = q.poll();
                if (node.left != null) {
                    q.offer(node.left);
                }
                if (node.right != null) {
                    q.offer(node.right);
                }
            }
            currentDepth++;
        }

        for (TreeNode node : q) {
            TreeNode oldLeft = node.left;
            TreeNode oldRight = node.right;
            node.left = new TreeNode(val);
            node.left.left = oldLeft;
            node.right = new TreeNode(val);
            node.right.right = oldRight;
        }
        return root;
    }
}

