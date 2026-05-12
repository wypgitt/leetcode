/*
 * LeetCode 1325 - Delete Leaves With a Given Value
 *
 * TreeNode is provided by LeetCode.
 */
class Solution {
    public TreeNode removeLeafNodes(TreeNode root, int target) {
        if (root == null) {
            return null;
        }

        root.left = removeLeafNodes(root.left, target);
        root.right = removeLeafNodes(root.right, target);

        if (root.left == null && root.right == null && root.val == target) {
            return null;
        }

        return root;
    }
}

/*
 * Interview explanation
 * ---------------------
 * Algorithm:
 * A deletion can turn a parent into a new target leaf, so the decision for a
 * node must happen after its children are processed. That is postorder DFS.
 *
 * Java data structures:
 * Recursion returns the new root of each subtree. Assigning
 * `root.left = ...` and `root.right = ...` reconnects pruned subtrees cleanly.
 *
 * Edge cases:
 * - The original root can be deleted, so the method returns the new root.
 * - Cascading deletions are handled because parents are checked after children.
 * - Null children return null.
 *
 * Complexity:
 * Time O(n), each node is visited once.
 * Space O(h), recursion stack height.
 */
