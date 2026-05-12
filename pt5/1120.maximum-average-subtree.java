import java.util.*;

class TreeNode {
    int val;
    TreeNode left;
    TreeNode right;

    TreeNode() {}

    TreeNode(int val) {
        this.val = val;
    }

    TreeNode(int val, TreeNode left, TreeNode right) {
        this.val = val;
        this.left = left;
        this.right = right;
    }
}

class Solution {
    private double best;

    public double maximumAverageSubtree(TreeNode root) {
        best = 0.0;
        dfs(root);
        return best;
    }

    private int[] dfs(TreeNode node) {
        if (node == null) {
            return new int[] {0, 0};
        }

        int[] left = dfs(node.left);
        int[] right = dfs(node.right);
        int sum = left[0] + right[0] + node.val;
        int count = left[1] + right[1] + 1;
        best = Math.max(best, (double) sum / count);
        return new int[] {sum, count};
    }
}

