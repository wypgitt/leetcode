/**
 * Algorithm:
 * Recursively pass exclusive lower and upper bounds inherited from all
 * ancestors. A node must satisfy low < node.val < high; children tighten one
 * side of the bound.
 *
 * Complexity:
 * Time O(n), recursion space O(h).
 */
class Solution {
    public boolean isValidBST(TreeNode root) {
        return dfs(root, Long.MIN_VALUE, Long.MAX_VALUE);
    }

    private boolean dfs(TreeNode node, long low, long high) {
        if (node == null) {
            return true;
        }
        if (!(low < node.val && node.val < high)) {
            return false;
        }
        return dfs(node.left, low, node.val) && dfs(node.right, node.val, high);
    }
}

