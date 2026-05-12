/*
 * LeetCode 1315 - Sum of Nodes with Even-Valued Grandparent
 *
 * TreeNode is provided by LeetCode.
 */
class Solution {
    public int sumEvenGrandparent(TreeNode root) {
        return dfs(root, null, null);
    }

    private int dfs(TreeNode node, TreeNode parent, TreeNode grandparent) {
        if (node == null) {
            return 0;
        }

        int total = 0;
        if (grandparent != null && grandparent.val % 2 == 0) {
            total += node.val;
        }

        total += dfs(node.left, node, parent);
        total += dfs(node.right, node, parent);
        return total;
    }
}

/*
 * Interview explanation
 * ---------------------
 * Algorithm:
 * During DFS, each node only needs two pieces of ancestor context: its parent
 * and grandparent. If the grandparent exists and has an even value, the current
 * node contributes to the sum.
 *
 * Java data structures:
 * Recursion is sufficient; no map or parent pointer structure is needed. Each
 * recursive call carries `parent` and `grandparent` references.
 *
 * Edge cases:
 * - The root and root's children have no grandparent.
 * - Empty tree returns 0.
 * - Parity check works independently of tree shape.
 *
 * Complexity:
 * Time O(n), every node is visited once.
 * Space O(h), for recursion stack height.
 */
