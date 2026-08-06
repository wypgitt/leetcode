/**
 * Algorithm:
 * Postorder DFS asks whether each subtree is univalue. A subtree is univalue if
 * both children are univalue and any existing child has the same value as the
 * current node.
 *
 * Complexity:
 * Time O(n), recursion space O(h).
 */
class Solution {
    private int count;

    public int countUnivalSubtrees(TreeNode root) {
        count = 0;
        dfs(root);
        return count;
    }

    private boolean dfs(TreeNode node) {
        if (node == null) {
            return true;
        }
        boolean leftOk = dfs(node.left);
        boolean rightOk = dfs(node.right);
        if (!leftOk || !rightOk) {
            return false;
        }
        if (node.left != null && node.left.val != node.val) {
            return false;
        }
        if (node.right != null && node.right.val != node.val) {
            return false;
        }
        count++;
        return true;
    }
}

