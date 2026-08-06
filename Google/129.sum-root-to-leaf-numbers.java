/**
 * Algorithm:
 * DFS carries the number formed by the current root-to-node path. At each node,
 * current = current * 10 + node.val. A leaf contributes that current value.
 *
 * Complexity:
 * Time O(n), recursion space O(h).
 */
class Solution {
    public int sumNumbers(TreeNode root) {
        return dfs(root, 0);
    }

    private int dfs(TreeNode node, int current) {
        if (node == null) {
            return 0;
        }
        current = current * 10 + node.val;
        if (node.left == null && node.right == null) {
            return current;
        }
        return dfs(node.left, current) + dfs(node.right, current);
    }
}

