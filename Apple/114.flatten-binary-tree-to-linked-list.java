/**
 * Algorithm:
 * Traverse in reverse preorder: right, left, root. `prev` is the head of the
 * already flattened suffix. For each node, point right to prev, clear left, and
 * move prev to the current node.
 *
 * Complexity:
 * Time O(n), recursion space O(h).
 */
class Solution {
    private TreeNode prev;

    public void flatten(TreeNode root) {
        prev = null;
        dfs(root);
    }

    private void dfs(TreeNode node) {
        if (node == null) {
            return;
        }
        dfs(node.right);
        dfs(node.left);
        node.right = prev;
        node.left = null;
        prev = node;
    }
}

