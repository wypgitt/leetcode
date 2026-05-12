/*
 * LeetCode 1372 - Longest ZigZag Path in a Binary Tree
 *
 * TreeNode is provided by LeetCode.
 */
class Solution {
    private int best;

    public int longestZigZag(TreeNode root) {
        best = 0;
        dfs(root);
        return best;
    }

    private int[] dfs(TreeNode node) {
        if (node == null) {
            return new int[] {-1, -1};
        }

        int[] left = dfs(node.left);
        int[] right = dfs(node.right);

        int goLeft = left[1] + 1;
        int goRight = right[0] + 1;
        best = Math.max(best, Math.max(goLeft, goRight));

        return new int[] {goLeft, goRight};
    }
}

/*
 * Interview explanation
 * ---------------------
 * Algorithm:
 * For each node, compute two values:
 * - longest ZigZag starting here if the first move goes left.
 * - longest ZigZag starting here if the first move goes right.
 * After moving left, the next move must go right, and vice versa.
 *
 * Java data structures:
 * A recursive DFS returns an `int[] {goLeft, goRight}`. Returning {-1, -1} for
 * null makes a leaf's two path lengths become 0 after adding 1.
 *
 * Edge cases:
 * - Single node returns 0 because path length counts edges.
 * - Straight chain usually gives at most 1 unless directions alternate.
 * - Null children are handled by the {-1, -1} base case.
 *
 * Complexity:
 * Time O(n).
 * Space O(h), recursion stack height.
 */
