import java.util.*;

/**
 * Algorithm:
 * Maintain a stack of the path to the next smallest node. Constructor pushes
 * the left spine. next pops one node and then pushes the left spine of its
 * right child.
 *
 * Java data structures:
 * ArrayDeque<TreeNode> is used as a stack.
 *
 * Complexity:
 * next and hasNext are O(1) amortized; space O(h).
 */
class BSTIterator {
    private final Deque<TreeNode> stack;

    public BSTIterator(TreeNode root) {
        stack = new ArrayDeque<>();
        pushLeft(root);
    }

    public int next() {
        TreeNode node = stack.pop();
        pushLeft(node.right);
        return node.val;
    }

    public boolean hasNext() {
        return !stack.isEmpty();
    }

    private void pushLeft(TreeNode node) {
        while (node != null) {
            stack.push(node);
            node = node.left;
        }
    }
}
